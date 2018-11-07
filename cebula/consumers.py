# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json, pdb
from asgiref.sync import async_to_sync

class TestConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Join room group
        self.group_name="likes"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async  def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'like_message',
                'message': message
            }
        )

    # Receive message from room group
    async def like_message(self, event):
        message = "%s님이 게시물을 좋아합니다."%event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

