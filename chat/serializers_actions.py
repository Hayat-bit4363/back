from rest_framework import serializers
from .models import Message, Status
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'is_edited', 'starred_by']

class StatusSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # Or full UserSerializer
    class Meta:
        model = Status
        fields = ['id', 'user', 'image', 'caption', 'created_at', 'expires_at']
