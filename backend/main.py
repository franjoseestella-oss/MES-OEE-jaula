"""Punto de entrada de la aplicación MES/OEE — App 2."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import get_settings
from database.session import create_tables, get_db
from database import repositories as repo
from models.events import MachineEvent
from mqtt.client import MQTTClient
from oee.scheduler import start_scheduler
from api.routes import router as api_router
from chatbot.routes import router as chat_router

logging.basicConfig(
    level=get_settings().log_level,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

_scheduler = None
_mqtt_client = None


def handle_mqtt_event(payload: dict) -> None:
    """Callback invocado por el cliente MQTT al recibir un evento."""
    try:
        machine_id = payload.get("machine_id") or payload.get("jaula_id") or "UNKNOWN"
        state = payload.get("state") or payload.get("estado") or "Unknown"
        ts_raw = payload.get("timestamp") or payload.get("ts") or ""
        ts = datetime.fromisoformat(ts_raw) if ts_raw else datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        # Extraer campos de secuencia
        secuencia_id = payload.get("secuencia_id")
        tiempo_teorico_s = payload.get("tiempo_teorico_s")
        duracion_real_s = payload.get("duracion_real_s")
        dentro_de_tiempo = payload.get("dentro_de_tiempo")
        error_val = payload.get("error")
        
        error_str = None
        severidad = None
        if error_val is not None:
            if isinstance(error_val, dict):
                error_str = json.dumps(error_val)
                severidad = error_val.get("severidad")
            else:
                error_str = str(error_val)
                try:
                    err_data = json.loads(error_str)
                    if isinstance(err_data, dict):
                        severidad = err_data.get("severidad")
                except Exception:
                    pass

        # Si el estado es Aborting, pero la severidad es aviso, no queremos cambiar el estado de la máquina
        # ya que según el protocolo sólo las alarmas "critico" cuentan como parada para la disponibilidad.
        if state == "Aborting" and severidad == "aviso":
            logger.info("Ignorando evento de estado Aborting para %s porque la severidad del error es 'aviso' (no crítico)", machine_id)
            return

        with get_db() as db:
            repo.save_event(
                db=db,
                machine_id=machine_id,
                state=state,
                ts=ts,
                piece_count=int(payload.get("piece_count", 0)),
                good_count=int(payload.get("good_count", 0)),
                bad_count=int(payload.get("bad_count", 0)),
                reason_code=payload.get("reason_code"),
                source="mqtt",
                secuencia_id=secuencia_id,
                tiempo_teorico_s=tiempo_teorico_s,
                duracion_real_s=duracion_real_s,
                dentro_de_tiempo=dentro_de_tiempo,
                error=error_str,
            )
        logger.info("Evento guardado: %s → %s (Secuencia: %s) @ %s", machine_id, state, secuencia_id, ts)
    except Exception as exc:
        logger.error("Error al guardar evento MQTT: %s", exc, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler, _mqtt_client

    logger.info("=== Iniciando MES/OEE App 2 ===")

    # Base de datos — arranque tolerante a fallos de conexión
    try:
        create_tables()
    except Exception as exc:
        logger.warning("BD no disponible al arrancar (%s). La app sigue activa.", exc)

    # Forzar todas las secuencias pendientes a NOK hasta el 23/06/2026
    try:
        from database.session import SessionLocal
        from database import repositories as repo
        with SessionLocal() as db:
            repo.force_all_pending_sequences_nok(db, max_date="20260623")
    except Exception as exc:
        logger.warning("No se pudieron forzar las secuencias a NOK al arrancar: %s", exc)

    # Asegurar tema oscuro en Grafana
    def ensure_grafana_dark_theme():
        import threading
        import time
        import urllib.request
        import base64
        import json

        def run():
            time.sleep(5)
            user = "fran.jose.estella@gmail.com"
            pw = "admin123"
            auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            }
            urls = [
                "http://grafana:3000/api/org/preferences",
                "http://grafana:3000/api/user/preferences",
                "http://localhost:3010/api/org/preferences",
                "http://localhost:3010/api/user/preferences"
            ]
            payload = {"theme": "dark"}
            data = json.dumps(payload).encode("utf-8")
            
            for i in range(12):
                success = False
                for url in urls:
                    try:
                        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            logger.info("Fuerza tema oscuro en Grafana: %s exitoso", url)
                            success = True
                    except Exception:
                        pass
                if success:
                    break
                time.sleep(10)

        threading.Thread(target=run, daemon=True).start()

    try:
        ensure_grafana_dark_theme()
    except Exception as exc:
        logger.warning("No se pudo iniciar el hilo para asegurar tema oscuro: %s", exc)

    # Scheduler de snapshots OEE
    try:
        _scheduler = start_scheduler()
    except Exception as exc:
        logger.warning("Scheduler no iniciado: %s", exc)

    # Cliente MQTT — no bloquea si el broker no está disponible
    try:
        _mqtt_client = MQTTClient(on_event=handle_mqtt_event)
        _mqtt_client.start()
    except Exception as exc:
        logger.warning("MQTT no disponible al arrancar (%s). Reintentará automáticamente.", exc)

    yield

    logger.info("=== Apagando MES/OEE App 2 ===")
    if _mqtt_client:
        _mqtt_client.stop()
    if _scheduler:
        _scheduler.shutdown(wait=False)


app = FastAPI(
    title="MES/OEE — Logisnext",
    version="1.0.0",
    description="Sistema de monitorización OEE en tiempo real para Logisnext.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de API
app.include_router(api_router)
app.include_router(chat_router)

# Archivos estáticos (interfaz chatbot)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def index():
    """Redirige al chatbot."""
    return FileResponse(str(static_dir / "chat.html"))


@app.get("/health")
def health_root():
    return {
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
        "mqtt_connected": _mqtt_client.is_connected if _mqtt_client else False,
    }
