import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"
        print(f"Notification WS: User {self.user.id} connected. Group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Notification WS: Received message: {data.get('type')} signal: {data.get('signal')}")
        
        if data.get('type') == 'call_signal':
            # Send to specific user
            target_user_id = data.get('target_user_id')
            print(f"Notification WS: Routing call_signal to user_{target_user_id}")
            if target_user_id:
                await self.channel_layer.group_send(
                    f"user_{target_user_id}",
                    {
                        "type": "notify",
                        "content": data
                    }
                )

    async def notify(self, event):
        await self.send(text_data=json.dumps(event["content"]))
