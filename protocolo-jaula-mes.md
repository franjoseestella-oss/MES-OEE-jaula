# Protocolo jaula-elevacion-hmi → MES-OEE-jaula

Spec de comunicación de estado entre la **jaula de elevación** (productor) y **MES/OEE** (consumidor).

## 1. Objetivo

MES-OEE-jaula necesita conocer en tiempo real el estado de la jaula para:
- Pintar la pantalla de plan de producción (State Timeline).
- Calcular OEE (disponibilidad / rendimiento / calidad).

La jaula debe informar, como mínimo, cuando: **se inicia una secuencia**, **se pausa**, y **la máquina entra en error**.

## 2. Roles

| App | Rol |
|-----|-----|
| jaula-elevacion-hmi | **Productor**: publica cada cambio de estado. |
| MES-OEE-jaula | **Consumidor**: se suscribe y reacciona. |

Comunicación desacoplada: la jaula no necesita saber si MES está escuchando.

## 3. Transporte: MQTT

MQTT encaja por ser pub/sub ligero, ideal para telemetría de estado, fácil en Python (`paho-mqtt`) y con broker (Mosquitto) en Docker.

- **QoS 1** (at least once) en los eventos de estado: MES no puede perder un cambio.
- **Mensaje retenido (retained)** en el topic de estado: una instancia de MES que se conecte de nuevo recibe al instante el último estado conocido.
- **LWT (Last Will and Testament)**: si el proceso de la jaula muere, el broker avisa a MES → hueco de disponibilidad para OEE.

## 4. Estados (enum canónico)

| Estado | Significado | Color en State Timeline | PackML |
|--------|-------------|--------------------------|--------|
| `EN_ESPERA` | Sin secuencia activa, esperando | Amarillo | IDLE |
| `SECUENCIA_INICIADA` | Arranque de secuencia | Verde | STARTING |
| `EN_PROCESO` | Ejecutando secuencia | Verde | EXECUTE |
| `PAUSADA` | Pausada por operario o condición | Ámbar / propio | HELD |
| `ERROR` | Máquina en error | Rojo | ABORTED |
| `FINALIZADA` | Secuencia terminada | Amarillo (con flag `dentro_de_tiempo`) | COMPLETE |
| *(offline vía LWT)* | Proceso de jaula caído | Gris / hueco disponibilidad | — |

## 5. Eventos (transiciones)

`inicio_secuencia` · `pausa` · `reanudacion` · `error` · `reset` (recuperación) · `fin_secuencia`

## 6. Topics

| Topic | Uso | QoS | Retained |
|-------|-----|-----|----------|
| `planta/jaula/{jaula_id}/estado` | Eventos de estado | 1 | Sí |
| `planta/jaula/{jaula_id}/conexion` | Disponibilidad (online/offline) | 1 | Sí (+ LWT) |

`{jaula_id}` p.ej. `JAULA-01`.

## 7. Esquema del mensaje de estado (JSON)

​```json
{
  "ts": "2026-06-21T10:32:14.512Z",
  "jaula_id": "JAULA-01",
  "estado": "EN_PROCESO",
  "evento": "inicio_secuencia",
  "secuencia_id": "SEC-03",
  "tiempo_teorico_s": 420,
  "duracion_real_s": null,
  "dentro_de_tiempo": null,
  "error": null,
  "operario": "fje"
}
​```

- `ts`: timestamp ISO-8601 UTC del cambio de estado.
- `secuencia_id`: `null` si no hay secuencia activa.
- `tiempo_teorico_s`: tiempo teórico de la secuencia (para el eje X del timeline).
- `duracion_real_s` / `dentro_de_tiempo`: se rellenan al `FINALIZADA`.
- `error`: objeto solo cuando `estado == ERROR` → `{ "codigo", "descripcion", "severidad" }`.

Mensaje de disponibilidad (`/conexion`): `{ "online": true|false, "ts": "..." }`. El `false` lo publica el broker vía LWT si la jaula cae.

## 8. Reglas de implementación

- La jaula publica **solo en cambios de estado** (no en bucle), salvo el keepalive de conexión.
- Todo mensaje lleva `ts` en UTC; jaula y MES sincronizados por NTP.
- MES persiste cada evento en la base de series temporales que alimenta el State Timeline y el OEE.
- `error.severidad`: `aviso` | `critico`. Solo `critico` cuenta como parada para disponibilidad.