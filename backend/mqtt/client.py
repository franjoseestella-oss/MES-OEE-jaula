"""Cliente MQTT con reconexión automática, QoS 1 y Last Will Testament."""

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from config import get_settings

logger = logging.getLogger(__name__)

PACKML_STATES = {
    "run": "Execute",
    "execute": "Execute",
    "pause": "Held",
    "held": "Held",
    "abortado": "Aborted",
    "aborted": "Aborted",
    "error": "Aborting",
    "aborting": "Aborting",
    "holding": "Holding",
    "idle": "Idle",
    "starting": "Starting",
    "stopping": "Stopping",
    "stopped": "Stopped",
    "completing": "Completing",
    "complete": "Complete",
    "resetting": "Resetting",
}


def normalize_state(raw: str) -> str:
    return PACKML_STATES.get(raw.lower().strip(), raw)


class MQTTClient:
    def __init__(self, on_event: Callable[[dict], None]):
        self._settings = get_settings()
        self._on_event = on_event
        self._client: Optional[mqtt.Client] = None
        self._lock = threading.Lock()
        self._connected = False

    def _topic(self, suffix: str) -> str:
        return f"{self._settings.mqtt_topic_prefix}/{suffix}"

    def start(self) -> None:
        s = self._settings
        lwt_payload = json.dumps({
            "machine_id": s.mqtt_topic_prefix.split("/")[-1],
            "state": "Disconnected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "piece_count": 0,
            "good_count": 0,
            "bad_count": 0,
        })

        client = mqtt.Client(
            client_id=s.mqtt_client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        client.will_set(
            topic=self._topic("estado"),
            payload=lwt_payload,
            qos=1,
            retain=True,
        )

        if s.mqtt_username:
            client.username_pw_set(s.mqtt_username, s.mqtt_password)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        client.reconnect_delay_set(min_delay=1, max_delay=30)

        client.connect_async(s.mqtt_broker_host, s.mqtt_broker_port, keepalive=60)
        client.loop_start()
        self._client = client
        logger.info("MQTT: conectando a %s:%s …", s.mqtt_broker_host, s.mqtt_broker_port)

    def stop(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._connected = True
            logger.info("MQTT: conectado.")
            # Suscribirse a estado y contadores de la máquina configurada
            client.subscribe(self._topic("estado"), qos=1)
            client.subscribe(self._topic("contadores"), qos=1)
            # Suscribirse a estado y conexión de todas las jaulas
            client.subscribe("planta/jaula/+/estado", qos=1)
            client.subscribe("planta/jaula/+/conexion", qos=1)
            logger.info("MQTT: suscrito a los temas de la máquina y de la jaula")
        else:
            logger.warning("MQTT: fallo de conexión, código %s", reason_code)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self._connected = False
        if reason_code != 0:
            logger.warning("MQTT: desconectado inesperadamente (código %s), reintentando…", reason_code)

    def _on_message(self, client, userdata, msg):
        try:
            raw = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("MQTT: payload inválido en %s: %s", msg.topic, exc)
            return

        # Extraer información de los tópicos de la jaula
        topic_parts = msg.topic.split("/")
        if len(topic_parts) >= 3 and topic_parts[0] == "planta" and topic_parts[1] == "jaula":
            jaula_id = topic_parts[2]
            raw["jaula_id"] = jaula_id
            if "ts" in raw and "timestamp" not in raw:
                raw["timestamp"] = raw["ts"]
            if topic_parts[-1] == "conexion":
                raw["state"] = "Idle" if raw.get("online") else "Disconnected"
            elif topic_parts[-1] == "estado":
                if "estado" in raw and "state" not in raw:
                    raw["state"] = raw["estado"]

        # Normalizar estado al vocabulario PackML
        if "state" in raw:
            raw["state"] = normalize_state(raw["state"])

        # Asegurar timestamp UTC
        if "timestamp" not in raw:
            raw["timestamp"] = datetime.now(timezone.utc).isoformat()
        else:
            try:
                dt = datetime.fromisoformat(raw["timestamp"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                raw["timestamp"] = dt.isoformat()
            except ValueError:
                raw["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Garantizar campos de contadores
        raw.setdefault("piece_count", 0)
        raw.setdefault("good_count", 0)
        raw.setdefault("bad_count", 0)

        logger.debug("MQTT evento: %s", raw)
        try:
            self._on_event(raw)
        except Exception as exc:
            logger.error("Error procesando evento MQTT: %s", exc, exc_info=True)

    @property
    def is_connected(self) -> bool:
        return self._connected
