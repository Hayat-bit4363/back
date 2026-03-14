import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware that takes a token from the query string and authenticates the user.
    Usage: ws://localhost:8000/ws/something/?token=<token>
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_params = scope.get("query_string", b"").decode()
        token = None
        
        for param in query_params.split("&"):
            if param.startswith("token="):
                token = param.split("=")[1]
                break

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token.payload.get("user_id")
                scope["user"] = await get_user(user_id)
            except Exception as e:
                print(f"JWT WebSocket Auth Error: {str(e)}")
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
