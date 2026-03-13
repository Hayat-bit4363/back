from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.all()

    def create(self, request, *args, **kwargs):
        # Check if conversation with participant exists
        participant_id = request.data.get('participant_id')
        if not participant_id:
            return Response({'error': 'participant_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        participant = get_object_or_404(User, id=participant_id)
        
        # Check existing conversation between these two
        # This logic assumes 1-on-1 for now
        conversations = Conversation.objects.filter(participants=request.user).filter(participants=participant)
        if conversations.exists():
            serializer = self.get_serializer(conversations.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, participant)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id).order_by('timestamp')

from rest_framework import parsers
class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        try:
            serializer.save(sender=self.request.user)
        except Exception as e:
            print(f"ERROR creating message: {str(e)}")
            raise e
