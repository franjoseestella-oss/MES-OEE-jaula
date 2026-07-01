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


def find_hmi_screenshots() -> list[str]:
    """Busca capturas HMI en la raíz del proyecto o directorios cercanos."""
    from pathlib import Path
    paths_to_try = [
        Path(__file__).resolve().parent.parent.parent,
        Path.cwd(),
        Path(__file__).resolve().parent.parent
    ]
    for p in paths_to_try:
        p1 = p / "media_user_1.png"
        p2 = p / "media_user_2.png"
        if p1.exists() and p2.exists():
            return [str(p1), str(p2)]
            
    # Fallback si solo se encuentra una
    for p in paths_to_try:
        p1 = p / "media_user_1.png"
        p2 = p / "media_user_2.png"
        found = []
        if p1.exists():
            found.append(str(p1))
        if p2.exists():
            found.append(str(p2))
        if found:
            return found
    return []


def archive_and_cleanup_screenshots(processed_paths: list[str]) -> None:
    """
    Mueve las capturas HMI procesadas a un directorio de archivo con marca de tiempo,
    y purga capturas archivadas antiguas para evitar agotar el espacio en disco.
    """
    import os
    import shutil
    from datetime import datetime, timedelta
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    archive_dir = project_root / "archive_screenshots"
    archive_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path_str in processed_paths:
        path = Path(path_str)
        if path.exists():
            dest_name = f"{path.stem}_{timestamp}{path.suffix}"
            dest_path = archive_dir / dest_name
            try:
                shutil.move(str(path), str(dest_path))
                logger.info("Archivada captura HMI procesada: %s -> %s", path.name, dest_name)
            except Exception as e:
                logger.error("Error al archivar %s: %s", path.name, e)

    # Limpieza de capturas archivadas con más de 24 horas de antigüedad
    retention_limit = datetime.now() - timedelta(hours=24)
    try:
        for f in archive_dir.glob("media_user_*"):
            if f.is_file():
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < retention_limit:
                    f.unlink()
                    logger.info("Purgada captura HMI antigua por retención: %s (modificada el %s)", f.name, mtime)
    except Exception as e:
        logger.error("Error al limpiar capturas HMI antiguas: %s", e)


def run_snapshot() -> None:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    window_minutes = 60  # ventana móvil de 1 h para el snapshot

    # Buscar y extraer OCR si hay capturas disponibles (una vez por ejecución del planificador)
    image_paths = find_hmi_screenshots()
    ocr_data = None
    if image_paths:
        logger.info("Scheduler ejecutando OCR sobre capturas HMI: %s", image_paths)
        try:
            from oee.ocr_parser import extract_metrics_from_images
            ocr_data = extract_metrics_from_images(image_paths)
        except Exception as exc:
            logger.error("Error al procesar OCR de HMI en el scheduler: %s", exc, exc_info=True)

    with get_db() as db:
        statuses = repo.get_all_machine_statuses(db)
        machine_ids = [s.machine_id for s in statuses] if statuses else []

        if not machine_ids:
            if image_paths:
                archive_and_cleanup_screenshots(image_paths)
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

            # Si hay datos de OCR, aplicarlos
            ocr_applied = False
            if ocr_data:
                if "availability" in ocr_data:
                    snap.availability = ocr_data["availability"]
                if "performance" in ocr_data:
                    snap.performance = ocr_data["performance"]
                if "quality" in ocr_data:
                    snap.quality = ocr_data["quality"]
                if "oee" in ocr_data:
                    snap.oee = ocr_data["oee"]
                if "good_pieces" in ocr_data:
                    snap.good_pieces = ocr_data["good_pieces"]
                if "total_pieces" in ocr_data:
                    snap.total_pieces = ocr_data["total_pieces"]
                if "shift_label" in ocr_data:
                    snap.shift_label = ocr_data["shift_label"]
                if "run_time_s" in ocr_data:
                    snap.run_time_s = ocr_data["run_time_s"]
                if "planned_time_s" in ocr_data:
                    snap.planned_time_s = ocr_data["planned_time_s"]
                ocr_applied = True
                logger.info("Métricas de snapshot actualizadas con OCR de la HMI para la máquina %s.", machine_id)

            repo.save_oee_snapshot(db, snap)
            logger.info(
                "Snapshot OEE [%s] (OCR=%s) OEE=%.1f%% A=%.1f%% R=%.1f%% C=%.1f%% Piezas=%s/%s Turno=%s",
                machine_id,
                ocr_applied,
                (snap.oee or 0) * 100,
                (snap.availability or 0) * 100,
                (snap.performance or 0) * 100,
                (snap.quality or 0) * 100,
                snap.good_pieces,
                snap.total_pieces,
                snap.shift_label,
            )

    # Archivar y limpiar capturas procesadas
    if image_paths:
        archive_and_cleanup_screenshots(image_paths)



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
