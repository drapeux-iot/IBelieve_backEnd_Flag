from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from django.utils.timezone import now
from game.models import Team, Flag

BROKER = "test.mosquitto.org"
TOPIC = "drapeau/capture"

def on_connect(client, userdata, flags, rc):
    print("✅ Connecté au broker MQTT")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        print(f"📩 Message reçu: {message}")

        team = Team.objects.filter(name=message).first()
        if team:
            flag = Flag.objects.first()
            if flag:
                flag.captured_by = team
                flag.timestamp = now()
                flag.save()
                print(f"🏁 {team.name} a capturé le drapeau !")
            else:
                print("⚠️ Aucun drapeau trouvé")
        else:
            print("❌ Joueur inconnu")

    except Exception as e:
        print(f"🚨 Erreur traitement MQTT: {e}")

class Command(BaseCommand):
    help = "Écoute les messages MQTT pour la capture du drapeau"

    def handle(self, *args, **kwargs):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, 1883, 60)
        client.loop_forever()
