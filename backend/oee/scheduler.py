"""Planificador de snapshots periódicos de OEE."""

import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from config import get_settings
from database.session import get_db
from database import repositories as repo
from models.events import OeeSnapshot
from oee.calculator import oee_for_window, oee_for_shift, EventRow

logger = logging.getLogger(__name__)


def _row_to_event(ev) -> EventRow:
    ts = ev.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return EventRow(
        machine_id=ev.machine_id,
        state=ev.state,
        timestamp=ts,
        piece_count=ev.piece_count or 0,
        good_count=ev.good_count or 0,
        bad_count=ev.bad_count or 0,
    )


def run_snapshot() -> None:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    window_minutes = 60  # ventana móvil de 1 h para el snapshot

    with get_db() as db:
        statuses = repo.get_all_machine_statuses(db)
        machine_ids = [s.machine_id for s in statuses] if statuses else []

        # Si no hay máquinas registradas aún, salir silenciosamente
        if not machine_ids:
            return

        for machine_id in machine_ids:
            since = now - timedelta(minutes=window_minutes)
            events_db = repo.get_events_in_range(db, machine_id, since, now)
            events = [_row_to_event(e) for e in events_db]

            result = oee_for_window(
                events=events,
                machine_id=machine_id,
                minutes=window_minutes,
                ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
                reference_ts=now,
            )

            snap = OeeSnapshot(
                machine_id=machine_id,
                ts=result.ts,
                window_minutes=result.window_minutes,
                availability=result.availability,
                performance=result.performance,
                quality=result.quality,
                oee=result.oee,
                planned_time_s=result.planned_time_s,
                run_time_s=result.run_time_s,
                total_pieces=result.total_pieces,
                good_pieces=result.good_pieces,
                ideal_cycle_time_s=result.ideal_cycle_time_s,
                shift_label=result.shift_label,
            )
            repo.save_oee_snapshot(db, snap)
            logger.info(
                "Snapshot OEE [%s] OEE=%.1f%% A=%.1f%% R=%.1f%% C=%.1f%%",
                machine_id,
                (result.oee or 0) * 100,
                (result.availability or 0) * 100,
                (result.performance or 0) * 100,
                (result.quality or 0) * 100,
            )


def start_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_snapshot,
        trigger="interval",
        seconds=settings.oee_snapshot_interval_seconds,
        id="oee_snapshot",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler de snapshots OEE iniciado (cada %ss).",
        settings.oee_snapshot_interval_seconds,
    )
    return scheduler
