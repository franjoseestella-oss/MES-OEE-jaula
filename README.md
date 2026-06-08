# LOGISNEXT — App 2 MES/OEE

Sistema de monitorización OEE en tiempo real para la planta Logisnext (Pruebas de elevación / Forklift).

## Arquitectura

```
App 1 (existente)
  └─ publica MQTT → Mosquitto
                        └─ Backend FastAPI (App 2)
                              ├─ guarda eventos en SQL Server (tablas mes_*)
                              ├─ calcula OEE cada 60s → mes_oee_snapshots
                              └─ expone API + chatbot
                                        └─ Grafana (lee mes_oee_snapshots)
```

- **MQTT** = tiempo real (estado de la máquina)
- **SQL Server** = histórico (App 1 lo escribe; App 2 lo lee en solo lectura + escribe sus propias tablas)

---

## Requisitos previos

- Docker Desktop con WSL2 o Docker Engine (Linux)
- ODBC Driver 18 for SQL Server accesible desde la red del contenedor
- Python 3.11+ (solo para correr los tests localmente, opcional)

---

## Arranque rápido

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales reales:
#   SQL_SERVER_HOST, SQL_SERVER_DATABASE, SQL_SERVER_USER, SQL_SERVER_PASSWORD
#   ANTHROPIC_API_KEY
```

### 2. Levantar servicios

```bash
docker-compose up --build -d
```

Servicios que arranca:
| Servicio   | URL / Puerto         |
|------------|----------------------|
| Backend    | http://localhost:8000 |
| Chatbot    | http://localhost:8000 (raíz) |
| Grafana    | http://localhost:3010 |
| Mosquitto  | localhost:1883 (MQTT) |

### 3. Verificar

```bash
curl http://localhost:8000/health
# {"status":"ok","mqtt_connected":true,...}
```

### 4. Grafana

- Abre http://localhost:3010
- Usuario: `admin` / Contraseña: la de `GF_SECURITY_ADMIN_PASSWORD` en tu `.env`
- El dashboard **LOGISNEXT — MES / OEE** aparece automáticamente en la carpeta _Logisnext MES_.

---

## Parar

```bash
docker-compose down
# Para eliminar también los volúmenes (datos de Grafana y Mosquitto):
docker-compose down -v
```

---

## Estructura del proyecto

```
.
├── .env.example            Variables de entorno (plantilla)
├── docker-compose.yml
├── mosquitto/
│   └── config/mosquitto.conf
├── grafana/
│   └── provisioning/
│       ├── datasources/sqlserver.yml
│       └── dashboards/oee_dashboard.json
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py             Punto de entrada FastAPI
    ├── config.py           Settings (pydantic-settings)
    ├── models/events.py    ORM SQLAlchemy (tablas mes_*)
    ├── database/
    │   ├── session.py      Engine + contexto de sesión
    │   └── repositories.py Lectura/escritura de datos
    ├── mqtt/client.py      Cliente paho-mqtt con LWT y reconexión
    ├── oee/
    │   ├── calculator.py   Lógica OEE (ventana móvil, turno, día)
    │   └── scheduler.py    Snapshots periódicos con APScheduler
    ├── api/routes.py       Endpoints REST (/api/v1/...)
    ├── chatbot/
    │   ├── tools.py        Herramientas parametrizadas para el LLM
    │   ├── agent.py        Agente Claude con bucle tool_use
    │   └── routes.py       Endpoint POST /api/v1/chat
    ├── static/chat.html    Interfaz web del chatbot (HMI oscuro)
    └── tests/
        └── test_oee_calculator.py
```

---

## Tests

```bash
cd backend
pip install -r requirements.txt
pip install pytest
pytest tests/ -v
```

Los tests cubren: solo Execute, Execute+Held, piezas malas, sin eventos, rendimiento > 1 y OEE completo.

---

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/machines` | Lista todas las máquinas |
| GET | `/api/v1/machines/{id}/status` | Estado en tiempo real |
| GET | `/api/v1/machines/{id}/oee/live?minutes=60` | OEE en ventana móvil |
| GET | `/api/v1/machines/{id}/oee/shift` | OEE del turno actual |
| GET | `/api/v1/machines/{id}/oee/history` | Historial de snapshots |
| GET | `/api/v1/machines/{id}/events` | Eventos en rango |
| GET | `/api/v1/machines/{id}/stops` | Causas de parada |
| POST | `/api/v1/chat` | Chatbot (ver esquema abajo) |
| GET | `/health` | Estado del servicio |

### Chatbot — esquema POST /api/v1/chat

```json
{
  "messages": [
    {"role": "user", "content": "¿Cuál es el OEE del turno actual?"}
  ],
  "machine_id": "MAQ-01"
}
```

---

## MQTT — Topics

| Topic | Descripción |
|-------|-------------|
| `planta/{linea}/{maquina}/estado` | Cambio de estado de la máquina |
| `planta/{linea}/{maquina}/contadores` | Actualización de contadores |

Payload de ejemplo:
```json
{
  "machine_id": "MAQ-01",
  "state": "Execute",
  "timestamp": "2026-06-08T10:15:30Z",
  "piece_count": 1240,
  "good_count": 1228,
  "bad_count": 12
}
```

---

## Modelo de estados (PackML)

| Estado App 1 | Estado PackML |
|---|---|
| run | Execute |
| pause | Held |
| abortado | Aborted |
| error (crítico) | Aborting |
| error (leve) | Holding |

Solo el tiempo en `Execute` cuenta como tiempo productivo.

---

## Turnos

| Turno | Horario |
|-------|---------|
| T1 | 06:00 – 14:00 |
| T2 | 14:00 – 22:00 |
| T3 | 22:00 – 06:00 |

---

## Variables de entorno relevantes

| Variable | Descripción |
|----------|-------------|
| `SQL_SERVER_HOST` | Host del SQL Server de App 1 |
| `MQTT_BROKER_HOST` | Host del broker (por defecto: `mosquitto`) |
| `MQTT_TOPIC_PREFIX` | Prefijo del topic, p.ej. `planta/linea1/MAQ-01` |
| `IDEAL_CYCLE_TIME_SECONDS` | Ciclo ideal en segundos por pieza |
| `OEE_SNAPSHOT_INTERVAL_SECONDS` | Frecuencia de snapshots (default 60s) |
| `ANTHROPIC_API_KEY` | Clave API de Claude para el chatbot |
