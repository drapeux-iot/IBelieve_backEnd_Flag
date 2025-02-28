import paho.mqtt.client as mqtt
import requests
import json

# Configuration
DJANGO_API_URL = "http://127.0.0.1:8000/capture_flag/"  # Endpoint pour capturer le drapeau

def on_message(client, userdata, msg):
    team_name = msg.payload.decode().strip()  # Récupère "Blue" ou "Red"
    print(f"📩 Message MQTT reçu: {team_name}")

    if team_name not in ["Blue", "Red"]:
        print("❌ Message inconnu, aucun traitement")
        return

    # Création du payload pour l'API Django
    data = {
        "team": team_name
    }

    # Envoyer la requête POST à Django pour capturer le drapeau
    try:
        response = requests.post(DJANGO_API_URL, json=data)
        if response.status_code == 200:
            print(f"✅ Drapeau capturé par {team_name} !")
        else:
            print(f"⚠️ Erreur API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Erreur de connexion à l'API Django: {e}")

# Configuration du client MQTT
client = mqtt.Client()
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)
client.subscribe("drapeau/capture")

print("📡 En attente des messages MQTT...")
client.loop_forever()
