from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentCreateView, LikePostView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('<int:pk>/like/', LikePostView.as_view(), name='like-post'),
]
