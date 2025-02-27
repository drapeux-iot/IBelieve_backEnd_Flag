from channels.generic.websocket import AsyncWebsocketConsumer
import json

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        # Rejoindre le groupe WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recevoir un message du WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Envoie un message à tous les clients du groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_to_game',
                'message': message
            }
        )

    # Envoi d'un message au WebSocket
    async def send_to_game(self, event):
        message = event['message']

        # Envoie le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
