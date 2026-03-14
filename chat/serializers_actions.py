from rest_framework import serializers
from .models import Message, Status
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'is_edited', 'starred_by']

from accounts.serializers import UserSerializer

class StatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Status
        fields = ['id', 'user', 'image', 'caption', 'created_at', 'expires_at']
        read_only_fields = ['expires_at']
