import paho.mqtt.client as mqtt
import requests
import json

# Configuration
DJANGO_API_URL = "http://127.0.0.1:8000/capture_flag/"  # Endpoint pour capturer le drapeau
LAST_GAME_URL = "http://127.0.0.1:8000/last_game/"  # Endpoint pour récupérer le dernier game_id

def get_last_game_id():
    """Récupère l'ID du dernier jeu en cours"""
    try:
        response = requests.get(LAST_GAME_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("game_id")  # Supposons que l'API renvoie {"game_id": 5}
        else:
            print(f"⚠️ Erreur API (last game): {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Erreur de connexion à l'API Django: {e}")
    return None  # Retourne None en cas d'erreur

def on_message(client, userdata, msg):
    team_name = msg.payload.decode().strip()  # Récupère "Blue" ou "Red"
    print(f"📩 Message MQTT reçu: {team_name}")

    if team_name not in ["Blue", "Red"]:
        print("❌ Message inconnu, aucun traitement")
        return

    # Récupérer le dernier game_id
    game_id = get_last_game_id()
    if game_id is None:
        print("⚠️ Impossible de récupérer le dernier game_id")
        return

    # Créer le payload pour l'API Django
    data = {
        "game_id": game_id,
        "team": team_name
    }

    # Envoyer la requête POST à Django
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
