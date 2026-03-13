from django.db import models
from django.conf import settings

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    audio = models.FileField(upload_to='chat_audio/', null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    starred_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='starred_messages', blank=True)
    deleted_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='deleted_messages', blank=True)
    is_dropped = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.timestamp}"

class Status(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='statuses', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='status_images/')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Status by {self.user} at {self.created_at}"
