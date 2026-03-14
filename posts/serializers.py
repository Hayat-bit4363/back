from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class CommentSerializer(serializers.ModelSerializer):
    author = UserFeedSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True) # Set read_only

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'text', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserFeedSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    shared_from = serializers.PrimaryKeyRelatedField(read_only=True) # For simple ID
    original_post = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at', 'likes_count', 'is_liked', 'comments', 'shared_from', 'original_post']

    def get_original_post(self, obj):
        if obj.shared_from:
            return PostSerializer(obj.shared_from, context=self.context).data
        return None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False
