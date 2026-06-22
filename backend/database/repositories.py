"""Acceso a datos — tablas propias de App 2 y consultas de solo lectura a App 1."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from models.events import MachineEvent, OeeSnapshot, MachineStatus
import logging

logger = logging.getLogger(__name__)


# ── Escritura de eventos ──────────────────────────────────────────────────────

def upsert_machine_status(db: Session, machine_id: str, state: str,
                          ts: datetime, piece_count: int,
                          good_count: int, bad_count: int,
                          connected: bool = True) -> None:
    status = db.get(MachineStatus, machine_id)
    if status is None:
        status = MachineStatus(machine_id=machine_id)
        db.add(status)
    status.state = state
    status.last_event_ts = ts
    status.connected = connected
    status.piece_count = piece_count
    status.good_count = good_count
    status.bad_count = bad_count
    status.updated_at = datetime.utcnow()


def save_event(db: Session, machine_id: str, state: str, ts: datetime,
               piece_count: int, good_count: int, bad_count: int,
               reason_code: Optional[str] = None, source: str = "mqtt",
               secuencia_id: Optional[str] = None, tiempo_teorico_s: Optional[int] = None,
               duracion_real_s: Optional[int] = None, dentro_de_tiempo: Optional[bool] = None,
               error: Optional[str] = None) -> MachineEvent:
    ev = MachineEvent(
        machine_id=machine_id,
        state=state,
        timestamp=ts,
        piece_count=piece_count,
        good_count=good_count,
        bad_count=bad_count,
        reason_code=reason_code,
        source=source,
        secuencia_id=secuencia_id,
        tiempo_teorico_s=tiempo_teorico_s,
        duracion_real_s=duracion_real_s,
        dentro_de_tiempo=dentro_de_tiempo,
        error=error,
    )
    db.add(ev)
    upsert_machine_status(db, machine_id, state, ts, piece_count, good_count, bad_count)
    return ev


def save_oee_snapshot(db: Session, snapshot: OeeSnapshot) -> OeeSnapshot:
    db.add(snapshot)
    return snapshot


# ── Consultas de estado en vivo ───────────────────────────────────────────────

def get_machine_status(db: Session, machine_id: str) -> Optional[MachineStatus]:
    return db.get(MachineStatus, machine_id)


def get_all_machine_statuses(db: Session) -> list[MachineStatus]:
    return db.query(MachineStatus).all()


# ── Consultas de eventos por rango de tiempo ─────────────────────────────────

def get_events_in_range(db: Session, machine_id: str,
                        since: datetime, until: datetime) -> list[MachineEvent]:
    return (
        db.query(MachineEvent)
        .filter(
            MachineEvent.machine_id == machine_id,
            MachineEvent.timestamp >= since,
            MachineEvent.timestamp <= until,
        )
        .order_by(MachineEvent.timestamp)
        .all()
    )


def get_latest_n_events(db: Session, machine_id: str, n: int = 100) -> list[MachineEvent]:
    return (
        db.query(MachineEvent)
        .filter(MachineEvent.machine_id == machine_id)
        .order_by(MachineEvent.timestamp.desc())
        .limit(n)
        .all()
    )


# ── Consultas de OEE ─────────────────────────────────────────────────────────

def get_oee_snapshots(db: Session, machine_id: str,
                      since: datetime, until: datetime) -> list[OeeSnapshot]:
    return (
        db.query(OeeSnapshot)
        .filter(
            OeeSnapshot.machine_id == machine_id,
            OeeSnapshot.ts >= since,
            OeeSnapshot.ts <= until,
        )
        .order_by(OeeSnapshot.ts)
        .all()
    )


def get_latest_oee_snapshot(db: Session, machine_id: str) -> Optional[OeeSnapshot]:
    return (
        db.query(OeeSnapshot)
        .filter(OeeSnapshot.machine_id == machine_id)
        .order_by(OeeSnapshot.ts.desc())
        .first()
    )


def get_oee_by_shift(db: Session, machine_id: str, shift_label: str,
                     date: datetime) -> Optional[OeeSnapshot]:
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    return (
        db.query(OeeSnapshot)
        .filter(
            OeeSnapshot.machine_id == machine_id,
            OeeSnapshot.shift_label == shift_label,
            OeeSnapshot.ts >= day_start,
            OeeSnapshot.ts < day_end,
        )
        .order_by(OeeSnapshot.ts.desc())
        .first()
    )


def get_stop_summary(db: Session, machine_id: str,
                     since: datetime, until: datetime) -> list[dict]:
    """Resumen de tiempo por reason_code para el chatbot."""
    rows = (
        db.query(
            MachineEvent.reason_code,
            func.count(MachineEvent.id).label("ocurrencias"),
        )
        .filter(
            MachineEvent.machine_id == machine_id,
            MachineEvent.timestamp >= since,
            MachineEvent.timestamp <= until,
            MachineEvent.reason_code.isnot(None),
        )
        .group_by(MachineEvent.reason_code)
        .order_by(func.count(MachineEvent.id).desc())
        .all()
    )
    return [{"reason_code": r.reason_code, "ocurrencias": r.ocurrencias} for r in rows]


def get_sequence_by_id(db: Session, sequence_id: int) -> Optional[dict]:
    """Gets a sequence record from dbo.LOG_TABLA by ID."""
    from config import get_settings
    settings = get_settings()
    try:
        query = text(f"SELECT id, NSECUENCIA, NBASTIDOR, NMODELO, FECHA_MONTAJE, OK_NOK FROM {settings.app1_log_table} WHERE id = :id")
        row = db.execute(query, {"id": sequence_id}).fetchone()
        if row:
            return {
                "id": int(row[0]) if row[0] is not None else None,
                "nsecuencia": int(row[1]) if row[1] is not None else None,
                "nbastidor": row[2],
                "nmodelo": row[3],
                "fecha_montaje": row[4],
                "ok_nok": row[5]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting sequence {sequence_id}: {e}", exc_info=True)
        return None


def force_sequence_ok(db: Session, sequence_id: int) -> bool:
    """Updates OK_NOK to 'OK' in dbo.LOG_TABLA for the given ID."""
    from config import get_settings
    settings = get_settings()
    try:
        query = text(f"UPDATE {settings.app1_log_table} SET OK_NOK = 'OK' WHERE id = :id")
        result = db.execute(query, {"id": sequence_id})
        db.commit()
        return result.rowcount > 0
    except Exception as e:
        logger.error(f"Error forcing sequence {sequence_id} to OK: {e}", exc_info=True)
        db.rollback()
        raise e


def get_pending_sequence_by_bastidor(db: Session, bastidor: str) -> Optional[dict]:
    """Gets details of a pending sequence from JAULA_ERP by bastidor."""
    try:
        query = text("""
            SELECT id, secuencia, bastidor, modelo, fecha_montaje, mastil 
            FROM JAULA_ERP 
            WHERE bastidor = :bastidor
        """)
        row = db.execute(query, {"bastidor": bastidor}).fetchone()
        if row:
            return {
                "id": row[0],
                "secuencia": row[1],
                "bastidor": row[2],
                "modelo": row[3],
                "fecha_montaje": row[4],
                "mastil": row[5]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting pending sequence {bastidor}: {e}", exc_info=True)
        return None


def force_sequence_nok(db: Session, bastidor: str) -> bool:
    """Inserts a single sequence from JAULA_ERP into LOG_TABLA as NOK by its bastidor."""
    from config import get_settings
    settings = get_settings()
    try:
        # Check if it exists in JAULA_ERP and is not already in LOG_TABLA
        check_query = text(f"""
            SELECT COUNT(*) FROM JAULA_ERP erp
            WHERE erp.bastidor = :bastidor
              AND erp.bastidor NOT IN (
                  SELECT DISTINCT log.NBASTIDOR 
                  FROM {settings.app1_log_table} log 
                  WHERE log.NBASTIDOR IS NOT NULL
              )
        """)
        exists = db.execute(check_query, {"bastidor": bastidor}).scalar()
        if not exists:
            return False

        # Execute insertion
        insert_query = text(f"""
            INSERT INTO {settings.app1_log_table} (
                id,
                OPERARIO,
                FECHA_MONTAJE,
                NSECUENCIA,
                NMODELO,
                NBASTIDOR,
                NMASTIL,
                ALTURA_MAX_INTERMEDIA,
                OK_NOK,
                TIEMPO_ELEVACION_MIN_SINCARGA,
                TIEMPO_ELEVACION_MAX_SINCARGA,
                TIEMPO_DESCENSO_MIN_SINCARGA,
                TIEMPO_DESCENSO_MAX_SINCARGA,
                TIEMPO_ELEVACION_MIN_CARGA,
                TIEMPO_ELEVACION_MAX_CARGA,
                TIEMPO_DESCENSO_MIN_CARGA,
                TIEMPO_DESCENSO_MAX_CARGA,
                PESO_PRUEBA
            )
            SELECT 
                (SELECT COALESCE(MAX(id), 0) + 1 FROM {settings.app1_log_table}),
                'FORZADO NOK',
                TRY_CAST(erp.fecha_montaje AS DATETIME),
                TRY_CAST(erp.secuencia AS FLOAT),
                erp.modelo,
                erp.bastidor,
                erp.mastil,
                TRY_CAST(erp.altura_max_interm AS FLOAT),
                'NOK',
                TRY_CAST(erp.tpo_elev_min_scarga AS FLOAT),
                TRY_CAST(erp.tpo_elev_max_scarga AS FLOAT),
                TRY_CAST(erp.tpo_desc_min_scarga AS FLOAT),
                TRY_CAST(erp.tpo_desc_max_scarga AS FLOAT),
                TRY_CAST(erp.tpo_elevac_min AS FLOAT),
                TRY_CAST(erp.tpo_elevac_max AS FLOAT),
                TRY_CAST(erp.tpo_descenso_min AS FLOAT),
                TRY_CAST(erp.tpo_descenso_max AS FLOAT),
                TRY_CAST(erp.peso_pruebas AS FLOAT)
            FROM JAULA_ERP erp
            WHERE erp.bastidor = :bastidor;
        """)
        result = db.execute(insert_query, {"bastidor": bastidor})
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error forcing single sequence {bastidor} to NOK: {e}", exc_info=True)
        db.rollback()
        raise e


def force_all_pending_sequences_nok(db: Session, max_date: str = "20260624") -> int:
    """Inserts all pending sequences from JAULA_ERP (where fecha_montaje <= max_date) 
    into LOG_TABLA as NOK, generating sequential IDs from the current MAX(id)."""
    from config import get_settings
    settings = get_settings()
    try:
        # Check if there are any records first to avoid errors and trace log
        check_query = text(f"""
            SELECT COUNT(*) FROM JAULA_ERP erp
            WHERE erp.fecha_montaje <= :max_date
              AND erp.bastidor NOT IN (
                  SELECT DISTINCT log.NBASTIDOR 
                  FROM {settings.app1_log_table} log 
                  WHERE log.NBASTIDOR IS NOT NULL
              )
        """)
        pending_count = db.execute(check_query, {"max_date": max_date}).scalar()
        if pending_count == 0:
            logger.info("No pending sequences to force to NOK up to date %s.", max_date)
            return 0

        # Execute the insert
        insert_query = text(f"""
            INSERT INTO {settings.app1_log_table} (
                id,
                OPERARIO,
                FECHA_MONTAJE,
                NSECUENCIA,
                NMODELO,
                NBASTIDOR,
                NMASTIL,
                ALTURA_MAX_INTERMEDIA,
                OK_NOK,
                TIEMPO_ELEVACION_MIN_SINCARGA,
                TIEMPO_ELEVACION_MAX_SINCARGA,
                TIEMPO_DESCENSO_MIN_SINCARGA,
                TIEMPO_DESCENSO_MAX_SINCARGA,
                TIEMPO_ELEVACION_MIN_CARGA,
                TIEMPO_ELEVACION_MAX_CARGA,
                TIEMPO_DESCENSO_MIN_CARGA,
                TIEMPO_DESCENSO_MAX_CARGA,
                PESO_PRUEBA
            )
            SELECT 
                (SELECT COALESCE(MAX(id), 0) FROM {settings.app1_log_table}) + ROW_NUMBER() OVER (ORDER BY TRY_CAST(erp.fecha_montaje AS DATE) ASC, erp.secuencia ASC),
                'FORZADO NOK',
                TRY_CAST(erp.fecha_montaje AS DATETIME),
                TRY_CAST(erp.secuencia AS FLOAT),
                erp.modelo,
                erp.bastidor,
                erp.mastil,
                TRY_CAST(erp.altura_max_interm AS FLOAT),
                'NOK',
                TRY_CAST(erp.tpo_elev_min_scarga AS FLOAT),
                TRY_CAST(erp.tpo_elev_max_scarga AS FLOAT),
                TRY_CAST(erp.tpo_desc_min_scarga AS FLOAT),
                TRY_CAST(erp.tpo_desc_max_scarga AS FLOAT),
                TRY_CAST(erp.tpo_elevac_min AS FLOAT),
                TRY_CAST(erp.tpo_elevac_max AS FLOAT),
                TRY_CAST(erp.tpo_descenso_min AS FLOAT),
                TRY_CAST(erp.tpo_descenso_max AS FLOAT),
                TRY_CAST(erp.peso_pruebas AS FLOAT)
            FROM JAULA_ERP erp
            WHERE erp.fecha_montaje <= :max_date
              AND erp.bastidor NOT IN (
                  SELECT DISTINCT log.NBASTIDOR 
                  FROM {settings.app1_log_table} log 
                  WHERE log.NBASTIDOR IS NOT NULL
              )
        """)
        result = db.execute(insert_query, {"max_date": max_date})
        db.commit()
        logger.info("Forced %d pending sequences <= %s to NOK state.", pending_count, max_date)
        return pending_count
    except Exception as e:
        logger.error(f"Error forcing all pending sequences to NOK: {e}", exc_info=True)
        db.rollback()
        raise e


