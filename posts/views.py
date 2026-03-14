from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Allow viewing all, but modify needs check in perm class or here
        return Post.objects.all()

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'status': 'unliked', 'likes_count': post.likes.count()})
        else:
            post.likes.add(request.user)
            return Response({'status': 'liked', 'likes_count': post.likes.count()})

class SharePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        original_post = get_object_or_404(Post, pk=pk)
        # Create a new post referencing the original
        new_post = Post.objects.create(
            author=request.user,
            content=f"Shared from {original_post.author.username}: {original_post.content}",
            shared_from=original_post,
            # We don't copy the image directly, we just reference the original
        )
        serializer = PostSerializer(new_post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
