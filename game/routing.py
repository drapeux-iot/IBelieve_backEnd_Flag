from django.urls import path
from game.consumer import CaptureFlagConsumer

websocket_urlpatterns = [
    path("ws/flag/", CaptureFlagConsumer.as_asgi()),
]
