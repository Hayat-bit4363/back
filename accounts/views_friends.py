from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification

User = get_user_model()

class PeopleListView(generics.ListAPIView):
    # List all users + handled search
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.request.query_params.get('search', '')
        users = User.objects.exclude(id=user.id)
        if query:
            users = users.filter(username__icontains=query)
        return users

class FriendRequestCreateView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)
        
        if receiver == request.user:
            return Response({'error': 'Cannot add self'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
            return Response({'error': 'Request already sent'}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.user.friends.filter(id=receiver.id).exists():
            return Response({'error': 'Already friends'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)
        
        # Notification Logic
        Notification.objects.create(
            user=receiver,
            content=f"{request.user.username} sent you a friend request."
        )
        
        # Send WebSocket Notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{receiver.id}",
            {
                "type": "notify",
                "content": {
                    "type": "friend_request",
                    "sender": request.user.username,
                    "request_id": friend_request.id
                }
            }
        )

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

class FriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Incoming requests
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')

class FriendRequestActionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action') # accept or reject
        friend_request = get_object_or_404(FriendRequest, id=pk, receiver=request.user)
        
        if action == 'accept':
            friend_request.status = 'accepted'
            friend_request.save()
            friend_request.sender.friends.add(friend_request.receiver)
            friend_request.receiver.friends.add(friend_request.sender) # Symmetrical
            
            # Notify Sender
            Notification.objects.create(
                user=friend_request.sender,
                content=f"{request.user.username} accepted your friend request."
            )
             # Send WebSocket Notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_request.sender.id}",
                {
                    "type": "notify",
                    "content": {
                        "type": "request_accepted",
                        "sender": request.user.username
                    }
                }
            )

            return Response({'status': 'accepted'})
            
        elif action == 'reject':
            friend_request.status = 'rejected'
            friend_request.save()
            # Or delete
            friend_request.delete()
            return Response({'status': 'rejected'})
            
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
