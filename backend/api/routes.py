from datetime import datetime, timezone, timedelta
from typing import Optional, List
from urllib.parse import quote
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
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


@router.get("/sequences/{sequence_id}/force-ok", response_class=HTMLResponse)
def force_sequence_ok_endpoint(
    sequence_id: int,
    request: Request,
    confirm: bool = Query(default=False),
    referer: Optional[str] = Query(default=None),
    db: Session = Depends(get_db_dep),
):
    default_redirect = "http://localhost:3010/d/mes-reg-v1/logisnext-e28094-registro?orgId=1"
    
    # Obtener referer de la cabecera o del parámetro
    ref_url = referer or request.headers.get("referer") or default_redirect
    
    if not confirm:
        # Obtener los datos de la secuencia
        seq = repo.get_sequence_by_id(db, sequence_id)
        if not seq:
            raise HTTPException(
                status_code=404, 
                detail=f"Secuencia con ID {sequence_id} no encontrada en la base de datos."
            )
        
        # Formatear la fecha
        fecha_str = "-"
        if seq.get("fecha_montaje"):
            dt = seq["fecha_montaje"]
            if isinstance(dt, datetime):
                fecha_str = dt.strftime("%d/%m/%Y %H:%M:%S")
            else:
                fecha_str = str(dt)
        
        nsecuencia = seq.get("nsecuencia") if seq.get("nsecuencia") is not None else "-"
        nbastidor = seq.get("nbastidor") if seq.get("nbastidor") is not None else "-"
        nmodelo = seq.get("nmodelo") if seq.get("nmodelo") is not None else "-"
        ok_nok = seq.get("ok_nok") if seq.get("ok_nok") is not None else "-"
        
        confirm_url = f"/api/v1/sequences/{sequence_id}/force-ok?confirm=true&referer={quote(ref_url)}"
        cancel_url = ref_url
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmar Cambio de Estado</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #111217;
            --card-bg: #181b1f;
            --border-color: #2c323d;
            --text-main: #f0f1f2;
            --text-muted: #9fa6b2;
            --primary: #2fd06a;
            --primary-hover: #26b558;
            --secondary: #e32636;
            --secondary-hover: #c41e2a;
            --neutral: #3a414f;
            --neutral-hover: #4a5262;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            width: 100%;
            max-width: 500px;
            padding: 32px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.3s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}

        .icon-container {{
            width: 56px;
            height: 56px;
            background-color: rgba(227, 38, 54, 0.1);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto 16px;
            border: 1px solid rgba(227, 38, 54, 0.2);
        }}

        .icon {{
            font-size: 24px;
            color: var(--secondary);
        }}

        h1 {{
            font-size: 22px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 8px;
            line-height: 1.3;
        }}

        .subtitle {{
            font-size: 14px;
            color: var(--text-muted);
        }}

        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 28px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}

        .details-row {{
            display: flex;
            border-bottom: 1px solid var(--border-color);
        }}

        .details-row:last-child {{
            border-bottom: none;
        }}

        .details-label {{
            flex: 1;
            padding: 12px 16px;
            background-color: rgba(255, 255, 255, 0.02);
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 600;
            border-right: 1px solid var(--border-color);
        }}

        .details-value {{
            flex: 1.5;
            padding: 12px 16px;
            font-size: 14px;
            color: var(--text-main);
        }}

        .badge {{
            background-color: rgba(227, 38, 54, 0.15);
            color: var(--secondary);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid rgba(227, 38, 54, 0.3);
        }}

        .actions {{
            display: flex;
            gap: 16px;
        }}

        .btn {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease-in-out;
            text-align: center;
            text-decoration: none;
            display: inline-block;
        }}

        .btn-confirm {{
            background-color: var(--primary);
            color: #0f1013;
        }}

        .btn-confirm:hover {{
            background-color: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(47, 208, 106, 0.3);
        }}

        .btn-cancel {{
            background-color: var(--neutral);
            color: var(--text-main);
            border: 1px solid var(--border-color);
        }}

        .btn-cancel:hover {{
            background-color: var(--neutral-hover);
            transform: translateY(-1px);
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="icon-container">
                <span class="icon">⚠️</span>
            </div>
            <h1>¿Forzar Secuencia a OK?</h1>
            <p class="subtitle">Esta acción modificará permanentemente el estado en la base de datos.</p>
        </div>

        <div class="details-table">
            <div class="details-row">
                <div class="details-label">ID Registro</div>
                <div class="details-value">{seq["id"]}</div>
            </div>
            <div class="details-row">
                <div class="details-label">Nº Secuencia</div>
                <div class="details-value">{nsecuencia}</div>
            </div>
            <div class="details-row">
                <div class="details-label">Bastidor</div>
                <div class="details-value">{nbastidor}</div>
            </div>
            <div class="details-row">
                <div class="details-label">Modelo</div>
                <div class="details-value">{nmodelo}</div>
            </div>
            <div class="details-row">
                <div class="details-label">Fecha Montaje</div>
                <div class="details-value">{fecha_str}</div>
            </div>
            <div class="details-row">
                <div class="details-label">Estado Actual</div>
                <div class="details-value"><span class="badge">{ok_nok}</span></div>
            </div>
        </div>

        <div class="actions">
            <a href="{cancel_url}" class="btn btn-cancel">Cancelar</a>
            <a href="{confirm_url}" class="btn btn-confirm">Sí, forzar a OK</a>
        </div>
    </div>
</body>
</html>
"""
        return HTMLResponse(content=html_content)
        
    else:
        # Ejecutar acción
        success = repo.force_sequence_ok(db, sequence_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Secuencia con ID {sequence_id} no encontrada en la base de datos."
            )
        
        return RedirectResponse(url=ref_url, status_code=303)


@router.get("/health")
def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

