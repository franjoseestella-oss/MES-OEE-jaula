import paho.mqtt.client as mqtt
import time
import sys

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker. Subscribing to '#'")
    client.subscribe("#")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode('utf-8', errors='ignore')}")
    print("-" * 40)

def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Try connecting to localhost
    try:
        client.connect("localhost", 1883, 60)
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)
        
    client.loop_start()
    print("Listening for 15 seconds...")
    time.sleep(15)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
