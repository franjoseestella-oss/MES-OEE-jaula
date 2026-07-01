import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone

def publish_test():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect("localhost", 1883, 60)
    
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "jaula_id": "JAULA-01",
        "estado": "EN_ESPERA",
        "evento": "reset",
        "secuencia_id": None,
        "error": None
    }
    
    topic = "planta/jaula/JAULA-01/estado"
    print(f"Publicando en {topic}:")
    print(json.dumps(payload, indent=2))
    
    client.publish(topic, json.dumps(payload), qos=1, retain=True)
    client.disconnect()
    print("Publicado con éxito.")

if __name__ == "__main__":
    publish_test()
