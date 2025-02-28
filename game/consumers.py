import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from .models import Game

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("game_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("game_updates", self.channel_name)

    async def receive(self, text_data):
        # Si besoin, gérer les messages WebSocket reçus ici
        pass

    async def send_game_update(self, event):
        game = await self.get_current_game()
        if game:
            flag_owner = game.flag.captured_by.name if game.flag and game.flag.captured_by else "Personne"
            blue_score = game.team_a.total_time_held_flag
            red_score = game.team_b.total_time_held_flag

            await self.send(text_data=json.dumps({
                "flag_owner": flag_owner,
                "scores": {
                    "Blue": blue_score,
                    "Red": red_score
                }
            }))

    async def get_current_game(self):
        return await Game.objects.filter(end_time__isnull=True).afirst()
