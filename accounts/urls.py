from django.urls import path
from .views import MyTokenObtainPairView, SearchUserView
from rest_framework_simplejwt.views import TokenRefreshView
from .views_update import UserUpdateView
from .views_friends import PeopleListView, FriendRequestCreateView, FriendRequestListView, FriendRequestActionView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', SearchUserView.as_view(), name='search_users'),
    path('me/', UserUpdateView.as_view(), name='user-update'),
    
    # Friends & People
    path('people/', PeopleListView.as_view(), name='people-list'),
    path('requests/', FriendRequestListView.as_view(), name='friend-requests'),
    path('requests/send/', FriendRequestCreateView.as_view(), name='send-request'),
    path('requests/<int:pk>/action/', FriendRequestActionView.as_view(), name='request-action'),
]
