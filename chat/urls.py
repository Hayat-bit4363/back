from django.urls import path
from .views import ConversationListCreateView, MessageListView, MessageCreateView
from .views_actions import MessageActionView, StarMessageView, StatusListView, StatusCreateView

urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/', MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/action/', MessageActionView.as_view(), name='message-action'),
    path('messages/<int:pk>/star/', StarMessageView.as_view(), name='message-star'),
    path('status/', StatusListView.as_view(), name='status-list'),
    path('status/create/', StatusCreateView.as_view(), name='status-create'),
]
