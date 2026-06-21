"""
Suscriptor MQTT en MES-OEE-jaula.
Repo: MES-OEE-jaula

Escucha el estado de todas las jaulas y lo traduce a color para el
State Timeline del plan de produccion.
  - planta/jaula/+/estado    -> evento de estado
  - planta/jaula/+/conexion  -> disponibilidad (online/offline)

Requisitos: pip install "paho-mqtt>=2.0"
"""
import json
import os

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("MQTT_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

TOPIC_ESTADO = "planta/jaula/+/estado"
TOPIC_CONEXION = "planta/jaula/+/conexion"

# Estado de la jaula -> color del State Timeline.
ESTADO_COLOR = {
    "EN_ESPERA": "amarillo",
    "SECUENCIA_INICIADA": "verde",
    "EN_PROCESO": "verde",
    "PAUSADA": "amarillo",   # o un color propio si quieres distinguir la pausa
    "ERROR": "rojo",
    "FINALIZADA": "amarillo",
}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe([(TOPIC_ESTADO, 1), (TOPIC_CONEXION, 1)])
        print("[mes] suscrito a estado y conexion de las jaulas")
    else:
        print(f"[mes] fallo de conexion: {reason_code}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
    except json.JSONDecodeError:
        print(f"[mes] payload no JSON en {msg.topic}")
        return

    if msg.topic.endswith("/conexion"):
        manejar_conexion(msg.topic, data)
    elif msg.topic.endswith("/estado"):
        manejar_estado(msg.topic, data)


def manejar_estado(topic, data):
    estado = data.get("estado")
    color = ESTADO_COLOR.get(estado, "gris")
    jaula = data.get("jaula_id")
    seq = data.get("secuencia_id")
    print(f"[mes] {jaula} {estado} ({color}) seq={seq}")

    # TODO: persistir en la base de series temporales que alimenta el
    # State Timeline y el calculo de OEE. Ejemplo:
    #   tsdb.write(jaula, seq, estado, color, data["ts"])

    if estado == "ERROR":
        err = data.get("error", {})
        if err.get("severidad") == "critico":
            print(f"[mes]   PARADA: {err.get('codigo')} {err.get('descripcion')}")


def manejar_conexion(topic, data):
    # topic = planta/jaula/{jaula_id}/conexion
    jaula = topic.split("/")[2]
    if data.get("online"):
        print(f"[mes] {jaula} ONLINE")
    else:
        # Jaula caida -> hueco de disponibilidad para el OEE.
        print(f"[mes] {jaula} OFFLINE (hueco de disponibilidad)")
        # TODO: marcar disponibilidad=0 desde data["ts"]


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mes-oee")
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_forever()


if __name__ == "__main__":
    main()

