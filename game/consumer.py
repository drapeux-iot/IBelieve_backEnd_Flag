import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import Flag

class CaptureFlagConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("capture_flag", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("capture_flag", self.channel_name)

    async def send_flag_update(self, event):
        flag = Flag.objects.first()
        captured_by = flag.captured_by.user.username if flag.captured_by else "None"
        await self.send(text_data=json.dumps({
            "captured_by": captured_by,
        }))
