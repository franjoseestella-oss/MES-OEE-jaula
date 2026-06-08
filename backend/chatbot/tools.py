"""Herramientas parametrizadas para el chatbot — nunca ejecuta SQL libre."""

from datetime import datetime, timezone, timedelta
from typing import Optional

from database.session import get_db
from database import repositories as repo
from oee.calculator import oee_for_window, oee_for_shift, EventRow, current_shift, SHIFT_SCHEDULE, shift_window


def _db_rows_to_events(rows) -> list[EventRow]:
    out = []
    for r in rows:
        ts = r.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        out.append(EventRow(
            machine_id=r.machine_id,
            state=r.state,
            timestamp=ts,
            piece_count=r.piece_count or 0,
            good_count=r.good_count or 0,
            bad_count=r.bad_count or 0,
        ))
    return out


# ── Tool handlers ─────────────────────────────────────────────────────────────

def tool_get_machine_status(machine_id: str) -> dict:
    with get_db() as db:
        s = repo.get_machine_status(db, machine_id)
        if not s:
            return {"error": f"Máquina '{machine_id}' no encontrada."}
        return {
            "machine_id": s.machine_id,
            "estado_actual": s.state,
            "conectada": s.connected,
            "ultima_actualizacion": s.updated_at.isoformat() if s.updated_at else None,
            "piezas_totales": s.piece_count,
            "piezas_buenas": s.good_count,
            "piezas_malas": s.bad_count,
        }


def tool_get_oee_live(machine_id: str, window_minutes: int = 60) -> dict:
    from config import get_settings
    settings = get_settings()
    window_minutes = max(1, min(window_minutes, 1440))
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=window_minutes)
    with get_db() as db:
        events_db = repo.get_events_in_range(db, machine_id, since, now)
    rows = _db_rows_to_events(events_db)
    result = oee_for_window(
        events=rows,
        machine_id=machine_id,
        minutes=window_minutes,
        ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
        reference_ts=now,
    )
    return {
        "machine_id": result.machine_id,
        "ventana_minutos": result.window_minutes,
        "turno": result.shift_label,
        "oee": round(result.oee * 100, 1) if result.oee is not None else None,
        "disponibilidad": round(result.availability * 100, 1) if result.availability is not None else None,
        "rendimiento": round(result.performance * 100, 1) if result.performance is not None else None,
        "calidad": round(result.quality * 100, 1) if result.quality is not None else None,
        "tiempo_en_marcha_s": round(result.run_time_s, 1),
        "tiempo_planificado_s": round(result.planned_time_s, 1),
        "piezas_totales": result.total_pieces,
        "piezas_buenas": result.good_pieces,
    }


def tool_get_oee_shift(machine_id: str, shift_label: Optional[str] = None) -> dict:
    from config import get_settings
    settings = get_settings()
    now = datetime.now(timezone.utc)
    label = shift_label or current_shift(now)
    if label not in SHIFT_SCHEDULE:
        return {"error": f"Turno '{label}' inválido. Usa T1, T2 o T3."}
    w_start, w_end = shift_window(now, label)
    elapsed_end = min(now, w_end)
    with get_db() as db:
        events_db = repo.get_events_in_range(db, machine_id, w_start, elapsed_end)
    rows = _db_rows_to_events(events_db)
    result = oee_for_window(
        events=rows,
        machine_id=machine_id,
        minutes=int((elapsed_end - w_start).total_seconds() / 60),
        ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
        reference_ts=elapsed_end,
    )
    result.shift_label = label
    return {
        "machine_id": result.machine_id,
        "turno": label,
        "oee": round(result.oee * 100, 1) if result.oee is not None else None,
        "disponibilidad": round(result.availability * 100, 1) if result.availability is not None else None,
        "rendimiento": round(result.performance * 100, 1) if result.performance is not None else None,
        "calidad": round(result.quality * 100, 1) if result.quality is not None else None,
        "tiempo_en_marcha_s": round(result.run_time_s, 1),
        "tiempo_planificado_s": round(result.planned_time_s, 1),
        "piezas_totales": result.total_pieces,
        "piezas_buenas": result.good_pieces,
        "inicio_turno": w_start.isoformat(),
        "fin_turno": w_end.isoformat(),
    }


def tool_get_oee_day(machine_id: str, date_str: Optional[str] = None) -> dict:
    from config import get_settings
    settings = get_settings()
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}
    else:
        day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = min(day + timedelta(days=1), datetime.now(timezone.utc))
    with get_db() as db:
        events_db = repo.get_events_in_range(db, machine_id, day, day_end)
    rows = _db_rows_to_events(events_db)
    minutes = int((day_end - day).total_seconds() / 60)
    result = oee_for_window(
        events=rows,
        machine_id=machine_id,
        minutes=minutes,
        ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
        reference_ts=day_end,
    )
    return {
        "machine_id": result.machine_id,
        "fecha": day.strftime("%Y-%m-%d"),
        "oee": round(result.oee * 100, 1) if result.oee is not None else None,
        "disponibilidad": round(result.availability * 100, 1) if result.availability is not None else None,
        "rendimiento": round(result.performance * 100, 1) if result.performance is not None else None,
        "calidad": round(result.quality * 100, 1) if result.quality is not None else None,
        "tiempo_en_marcha_s": round(result.run_time_s, 1),
        "piezas_totales": result.total_pieces,
        "piezas_buenas": result.good_pieces,
    }


def tool_get_stop_reasons(machine_id: str, hours: int = 8) -> dict:
    hours = max(1, min(hours, 168))
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)
    with get_db() as db:
        summary = repo.get_stop_summary(db, machine_id, since, now)
    return {
        "machine_id": machine_id,
        "periodo_horas": hours,
        "causas_parada": summary,
    }


def tool_list_machines() -> dict:
    with get_db() as db:
        statuses = repo.get_all_machine_statuses(db)
    return {
        "maquinas": [
            {"machine_id": s.machine_id, "estado": s.state, "conectada": s.connected}
            for s in statuses
        ]
    }


# ── Registro de herramientas para Claude ─────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_machine_status",
        "description": "Devuelve el estado actual en tiempo real de una máquina: estado PackML, conexión, contadores de piezas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string", "description": "ID de la máquina, p.ej. 'MAQ-01'"}
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "get_oee_live",
        "description": "Calcula el OEE en tiempo real para una ventana móvil de minutos indicados (por defecto 60 min).",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string"},
                "window_minutes": {"type": "integer", "description": "Duración de la ventana en minutos (1-1440). Por defecto 60."},
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "get_oee_shift",
        "description": "Calcula el OEE del turno actual o del turno indicado (T1, T2, T3).",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string"},
                "shift_label": {"type": "string", "enum": ["T1", "T2", "T3"], "description": "Turno (T1=06-14h, T2=14-22h, T3=22-06h). Si se omite, usa el turno actual."},
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "get_oee_day",
        "description": "Calcula el OEE acumulado de un día completo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string"},
                "date_str": {"type": "string", "description": "Fecha en formato YYYY-MM-DD. Si se omite, usa hoy."},
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "get_stop_reasons",
        "description": "Devuelve el resumen de causas de parada agrupadas por reason_code en las últimas N horas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string"},
                "hours": {"type": "integer", "description": "Horas hacia atrás (1-168). Por defecto 8."},
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "list_machines",
        "description": "Lista todas las máquinas registradas con su estado y conexión.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

TOOL_HANDLERS = {
    "get_machine_status": lambda inp: tool_get_machine_status(**inp),
    "get_oee_live": lambda inp: tool_get_oee_live(**inp),
    "get_oee_shift": lambda inp: tool_get_oee_shift(**inp),
    "get_oee_day": lambda inp: tool_get_oee_day(**inp),
    "get_stop_reasons": lambda inp: tool_get_stop_reasons(**inp),
    "list_machines": lambda inp: tool_list_machines(),
}
