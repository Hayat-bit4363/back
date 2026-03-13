from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Message, Status
from .serializers_actions import MessageActionSerializer, StatusSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

class MessageActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        # Edit Message
        message = get_object_or_404(Message, pk=pk, sender=request.user)
        text = request.data.get('text')
        if text:
            message.text = text
            message.is_edited = True
            message.save()
            return Response({'message': 'Message edited', 'text': message.text})
        return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete for everyone or me?
        delete_type = request.query_params.get('type', 'me') # 'me' or 'everyone'
        message = get_object_or_404(Message, pk=pk)
        
        if delete_type == 'everyone':
            if message.sender == request.user:
                message.is_dropped = True
                message.save()
                return Response({'message': 'Message deleted for everyone'})
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        else: # delete for me
            message.deleted_by.add(request.user)
            return Response({'message': 'Message deleted for you'})

class StarMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        if request.user in message.starred_by.all():
            message.starred_by.remove(request.user)
            return Response({'message': 'Unstarred'})
        else:
            message.starred_by.add(request.user)
            return Response({'message': 'Starred'})

class StatusCreateView(generics.CreateAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Expires in 24 hours
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        serializer.save(user=self.request.user, expires_at=expires_at)
