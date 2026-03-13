from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    friend_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'about', 'avatar', 'wallpaper', 'is_verified', 'friend_status')

    def get_friend_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        if obj == request.user:
            return 'self'
        
        if request.user.friends.filter(id=obj.id).exists():
            return 'friend'
        
        # Check pending requests
        if FriendRequest.objects.filter(sender=request.user, receiver=obj, status='pending').exists():
            return 'request_sent'
        
        if FriendRequest.objects.filter(sender=obj, receiver=request.user, status='pending').exists():
            return 'request_received'
            
        return 'none'

from .models import FriendRequest, OTPRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = '__all__'

from .utils import send_verification_email

class SendOTPSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        token['avatar'] = user.avatar.url if user.avatar else None
        return token
