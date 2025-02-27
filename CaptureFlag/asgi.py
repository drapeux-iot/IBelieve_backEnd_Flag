import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from game import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CaptureFlag.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/game/<int:game_id>/", consumers.GameConsumer.as_asgi()),
        ])
    ),
})
