from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from notifications.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        conversation = instance.conversation
        for participant in conversation.participants.all():
            if participant != instance.sender:
                # Create Notification
                notification = Notification.objects.create(
                    user=participant,
                    content=f"New message from {instance.sender.username}: {instance.text[:30]}..."
                )
                
                # Send to WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{participant.id}",
                    {
                        "type": "notify",
                        "content": {
                            "type": "notification",
                            "notification": {
                                "id": notification.id,
                                "content": notification.content,
                                "timestamp": str(notification.timestamp),
                                "conversation_id": conversation.id,
                                "sender": instance.sender.username,
                            }
                        }
                    }
                )
