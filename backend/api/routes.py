from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import get_db_dep
from database import repositories as repo
from oee.calculator import oee_for_window, oee_for_shift, EventRow, current_shift
from config import get_settings

router = APIRouter(prefix="/api/v1")


# ── Schemas de respuesta ──────────────────────────────────────────────────────

class MachineStatusResponse(BaseModel):
    machine_id: str
    state: str
    last_event_ts: Optional[datetime]
    connected: bool
    piece_count: int
    good_count: int
    bad_count: int

    class Config:
        from_attributes = True


class OeeResponse(BaseModel):
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
    shift_label: Optional[str]


class OeeSnapshotResponse(BaseModel):
    machine_id: str
    ts: datetime
    oee: Optional[float]
    availability: Optional[float]
    performance: Optional[float]
    quality: Optional[float]
    shift_label: Optional[str]
    total_pieces: int
    good_pieces: int

    class Config:
        from_attributes = True


class StopReasonResponse(BaseModel):
    reason_code: str
    ocurrencias: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _db_events_to_rows(events) -> list[EventRow]:
    rows = []
    for ev in events:
        ts = ev.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        rows.append(EventRow(
            machine_id=ev.machine_id,
            state=ev.state,
            timestamp=ts,
            piece_count=ev.piece_count or 0,
            good_count=ev.good_count or 0,
            bad_count=ev.bad_count or 0,
        ))
    return rows


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/machines", response_model=List[MachineStatusResponse])
def list_machines(db: Session = Depends(get_db_dep)):
    return repo.get_all_machine_statuses(db)


@router.get("/machines/{machine_id}/status", response_model=MachineStatusResponse)
def machine_status(machine_id: str, db: Session = Depends(get_db_dep)):
    status = repo.get_machine_status(db, machine_id)
    if not status:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return status


@router.get("/machines/{machine_id}/oee/live", response_model=OeeResponse)
def oee_live(
    machine_id: str,
    minutes: int = Query(default=60, ge=1, le=1440),
    db: Session = Depends(get_db_dep),
):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=minutes)
    events_db = repo.get_events_in_range(db, machine_id, since, now)
    rows = _db_events_to_rows(events_db)
    result = oee_for_window(
        events=rows,
        machine_id=machine_id,
        minutes=minutes,
        ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
        reference_ts=now,
    )
    return OeeResponse(
        machine_id=result.machine_id,
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
        shift_label=result.shift_label,
    )


@router.get("/machines/{machine_id}/oee/shift", response_model=OeeResponse)
def oee_shift(machine_id: str, db: Session = Depends(get_db_dep)):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    events_db = repo.get_latest_n_events(db, machine_id, n=2000)
    rows = _db_events_to_rows(events_db)
    result = oee_for_shift(
        events=rows,
        machine_id=machine_id,
        ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
        reference_ts=now,
    )
    return OeeResponse(
        machine_id=result.machine_id,
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
        shift_label=result.shift_label,
    )


@router.get("/machines/{machine_id}/oee/history", response_model=List[OeeSnapshotResponse])
def oee_history(
    machine_id: str,
    since: datetime = Query(default=None),
    until: datetime = Query(default=None),
    db: Session = Depends(get_db_dep),
):
    now = datetime.now(timezone.utc)
    _until = until or now
    _since = since or (now - timedelta(hours=24))
    snaps = repo.get_oee_snapshots(db, machine_id, _since, _until)
    return snaps


@router.get("/machines/{machine_id}/events", response_model=List[dict])
def machine_events(
    machine_id: str,
    since: Optional[datetime] = Query(default=None),
    until: Optional[datetime] = Query(default=None),
    limit: int = Query(default=200, le=2000),
    db: Session = Depends(get_db_dep),
):
    now = datetime.now(timezone.utc)
    _until = until or now
    _since = since or (now - timedelta(hours=8))
    events = repo.get_events_in_range(db, machine_id, _since, _until)
    return [
        {
            "id": e.id,
            "machine_id": e.machine_id,
            "state": e.state,
            "timestamp": e.timestamp,
            "piece_count": e.piece_count,
            "good_count": e.good_count,
            "bad_count": e.bad_count,
            "reason_code": e.reason_code,
        }
        for e in events[:limit]
    ]


@router.get("/machines/{machine_id}/stops", response_model=List[StopReasonResponse])
def stop_reasons(
    machine_id: str,
    since: Optional[datetime] = Query(default=None),
    until: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db_dep),
):
    now = datetime.now(timezone.utc)
    _until = until or now
    _since = since or (now - timedelta(hours=8))
    return repo.get_stop_summary(db, machine_id, _since, _until)


@router.get("/sequences/{sequence_id}/force-ok")
def force_sequence_ok_endpoint(
    sequence_id: int,
    request: Request,
    db: Session = Depends(get_db_dep),
):
    success = repo.force_sequence_ok(db, sequence_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Secuencia con ID {sequence_id} no encontrada en la base de datos.")
    
    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=303)
    
    default_redirect = "http://localhost:3010/d/mes-reg-v1/logisnext-e28094-registro?orgId=1"
    return RedirectResponse(url=default_redirect, status_code=303)


@router.get("/health")
def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

