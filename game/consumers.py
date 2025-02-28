import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FlagConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'flag_updates'

        # Rejoindre le groupe de diffusion
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe de diffusion
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recevoir un message depuis WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        team = text_data_json['team']

        # Envoi d'un message à tous les membres du groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'flag_status',
                'team': team,
            }
        )

    # Recevoir un message depuis le groupe
    async def flag_status(self, event):
        team = event['team']

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'team': team
        }))
