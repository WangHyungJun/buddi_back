# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json, pdb
from asgiref.sync import async_to_sync

class TestConsumer(WebsocketConsumer):

    def connect(self):
        # Join room group
        self.group_name="likes"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'like_message',
                'message': message
            }
        )

    # Receive message from room group
    def like_message(self, event):
        message = "%s님이 게시물을 좋아합니다."%event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

