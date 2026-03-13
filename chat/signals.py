from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import MessageSerializer

@receiver(post_save, sender=Message)
def broadcast_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{instance.conversation.id}'
        
        # Serialize message
        serializer = MessageSerializer(instance)
        message_data = serializer.data

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': message_data 
            }
        )
