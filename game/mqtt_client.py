import paho.mqtt.client as mqtt
import json
from django.utils.timezone import now
from .models import Player, Flag

BROKER = "test.mosquitto.org"
TOPIC = "drapeau/capture"

def on_connect(client, userdata, flags, rc):
    print("Connecté au broker MQTT")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        print(f"Message reçu: {message}")

        player = Player.objects.filter(user__username=message).first()
        if player:
            flag = Flag.objects.first()
            flag.captured_by = player
            flag.timestamp = now()
            flag.save()
            print(f"{player.user.username} a capturé le drapeau !")
        else:
            print("Joueur inconnu")

    except Exception as e:
        print(f"Erreur traitement MQTT: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()
