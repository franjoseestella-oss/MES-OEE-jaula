import paho.mqtt.client as mqtt
import time
import sys

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")
    print("-" * 50)

def listen():
    print("Conectando al broker MQTT local para escuchar todos los mensajes (#) durante 15s...")
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    try:
        client.connect("localhost", 1883, 60)
    except Exception as e:
        print(f"Error al conectar a localhost: {e}")
        # Intentar conectar a la IP del contenedor si se ejecuta desde docker, pero este script se ejecuta localmente.
        sys.exit(1)
        
    client.subscribe("#", qos=0)
    client.loop_start()
    time.sleep(15)
    client.loop_stop()
    client.disconnect()
    print("Finalizado.")

if __name__ == "__main__":
    listen()
