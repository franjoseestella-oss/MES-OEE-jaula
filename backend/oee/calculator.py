"""Motor de cálculo OEE — ventana móvil, turno y día.

Fórmulas:
  Disponibilidad = tiempo en Execute / tiempo planificado
  Rendimiento    = (ciclo_ideal × piezas_totales) / tiempo en Execute
  Calidad        = piezas_buenas / piezas_totales
  OEE            = Disponibilidad × Rendimiento × Calidad
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

logger = logging.getLogger(__name__)

EXECUTE_STATE = "Execute"

SHIFT_SCHEDULE = {
    "T1": (6, 14),
    "T2": (14, 22),
    "T3": (22, 6),   # cruza medianoche
}


@dataclass
class OeeResult:
    machine_id: str
    ts: datetime
    window_minutes: int
    availability: Optional[float]
    performance: Optional[float]
    quality: Optional[float]
    oee: Optional[float]
    planned_time_s: float
    run_time_s: float
    total_pieces: int
    good_pieces: int
    ideal_cycle_time_s: float
    shift_label: Optional[str] = None


@dataclass
class EventRow:
    """Representa un evento de estado (de la BD o de MQTT en memoria)."""
    machine_id: str
    state: str
    timestamp: datetime
    piece_count: int = 0
    good_count: int = 0
    bad_count: int = 0


def _safe_div(num: float, den: float) -> Optional[float]:
    if den <= 0:
        return None
    return min(num / den, 1.0)


def current_shift(ts: datetime) -> str:
    h = ts.hour
    for label, (start, end) in SHIFT_SCHEDULE.items():
        if start < end:
            if start <= h < end:
                return label
        else:  # cruza medianoche
            if h >= start or h < end:
                return label
    return "T1"


def shift_window(ts: datetime, shift_label: str) -> tuple[datetime, datetime]:
    """Devuelve (inicio, fin) del turno para la fecha de ts."""
    start_h, end_h = SHIFT_SCHEDULE[shift_label]
    day = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    shift_start = day.replace(hour=start_h)
    if start_h < end_h:
        shift_end = day.replace(hour=end_h)
    else:
        # T3: empieza en el día anterior si ts.hour < end_h
        if ts.hour < end_h:
            shift_start = (day - timedelta(days=1)).replace(hour=start_h)
        shift_end = day.replace(hour=end_h)
    return shift_start, shift_end


def calculate_oee(
    events: Sequence[EventRow],
    window_start: datetime,
    window_end: datetime,
    ideal_cycle_time_s: float,
    machine_id: str,
    window_minutes: int,
    shift_label: Optional[str] = None,
) -> OeeResult:
    """Calcula OEE a partir de una lista de eventos ordenados por timestamp."""

    planned_time_s = (window_end - window_start).total_seconds()
    run_time_s = 0.0

    if not events:
        return OeeResult(
            machine_id=machine_id, ts=window_end,
            window_minutes=window_minutes,
            availability=None, performance=None, quality=None, oee=None,
            planned_time_s=planned_time_s, run_time_s=0,
            total_pieces=0, good_pieces=0,
            ideal_cycle_time_s=ideal_cycle_time_s,
            shift_label=shift_label,
        )

    # Recortar eventos al rango [window_start, window_end]
    clipped = [e for e in events if window_start <= e.timestamp <= window_end]
    if not clipped:
        clipped = events  # fallback: usar todos y recortar lógicamente

    # Calcular tiempo en Execute sumando duración de cada intervalo
    for i, ev in enumerate(clipped):
        t_start = max(ev.timestamp, window_start)
        t_end = clipped[i + 1].timestamp if i + 1 < len(clipped) else window_end
        t_end = min(t_end, window_end)
        duration = (t_end - t_start).total_seconds()
        if ev.state == EXECUTE_STATE and duration > 0:
            run_time_s += duration

    # Contadores de piezas — diferencia entre primer y último evento del rango
    first_ev = clipped[0]
    last_ev = clipped[-1]
    total_pieces = max(last_ev.piece_count - first_ev.piece_count, 0)
    good_pieces = max(last_ev.good_count - first_ev.good_count, 0)

    availability = _safe_div(run_time_s, planned_time_s)
    performance = _safe_div(ideal_cycle_time_s * total_pieces, run_time_s) if run_time_s > 0 else None
    quality = _safe_div(good_pieces, total_pieces) if total_pieces > 0 else None

    if availability is not None and performance is not None and quality is not None:
        oee = availability * performance * quality
    else:
        oee = None

    return OeeResult(
        machine_id=machine_id,
        ts=window_end,
        window_minutes=window_minutes,
        availability=availability,
        performance=performance,
        quality=quality,
        oee=oee,
        planned_time_s=planned_time_s,
        run_time_s=run_time_s,
        total_pieces=total_pieces,
        good_pieces=good_pieces,
        ideal_cycle_time_s=ideal_cycle_time_s,
        shift_label=shift_label,
    )


def oee_for_window(
    events: Sequence[EventRow],
    machine_id: str,
    minutes: int,
    ideal_cycle_time_s: float,
    reference_ts: Optional[datetime] = None,
) -> OeeResult:
    """OEE en ventana móvil de `minutes` minutos hasta ahora (o reference_ts)."""
    now = reference_ts or datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=minutes)
    return calculate_oee(
        events=events,
        window_start=window_start,
        window_end=now,
        ideal_cycle_time_s=ideal_cycle_time_s,
        machine_id=machine_id,
        window_minutes=minutes,
        shift_label=current_shift(now),
    )


def oee_for_shift(
    events: Sequence[EventRow],
    machine_id: str,
    ideal_cycle_time_s: float,
    reference_ts: Optional[datetime] = None,
) -> OeeResult:
    """OEE del turno actual (o del turno de reference_ts)."""
    now = reference_ts or datetime.now(timezone.utc)
    label = current_shift(now)
    w_start, w_end = shift_window(now, label)
    elapsed_end = min(now, w_end)
    elapsed_minutes = int((elapsed_end - w_start).total_seconds() / 60)
    return calculate_oee(
        events=events,
        window_start=w_start,
        window_end=elapsed_end,
        ideal_cycle_time_s=ideal_cycle_time_s,
        machine_id=machine_id,
        window_minutes=elapsed_minutes,
        shift_label=label,
    )
