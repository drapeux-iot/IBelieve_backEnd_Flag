from django.urls import re_path
from game.consumers import FlagConsumer  # Importer ton consumer WebSocket

websocket_urlpatterns = [
    re_path(r'ws/game/$', FlagConsumer.as_asgi()),
]
