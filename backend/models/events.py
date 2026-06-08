"""SQLAlchemy ORM models — tablas propias de App 2 (métricas y snapshots).
Las tablas de App 1 (histórico) se consultan en solo lectura desde db/repositories.py."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, Index
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class MachineEvent(Base):
    """Evento de estado recibido por MQTT y/o leído de SQL Server."""
    __tablename__ = "mes_machine_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), nullable=False, index=True)
    state = Column(String(30), nullable=False)          # estado PackML
    timestamp = Column(DateTime, nullable=False, index=True)
    piece_count = Column(Integer, default=0)            # acumulado
    good_count = Column(Integer, default=0)
    bad_count = Column(Integer, default=0)
    reason_code = Column(String(50), nullable=True)
    source = Column(String(10), default="mqtt")         # "mqtt" | "sql"
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_mes_events_machine_ts", "machine_id", "timestamp"),
    )


class OeeSnapshot(Base):
    """Snapshot periódico de OEE — lo consume Grafana."""
    __tablename__ = "mes_oee_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), nullable=False, index=True)
    ts = Column(DateTime, nullable=False, index=True)   # instante del snapshot
    window_minutes = Column(Integer, default=60)        # ventana de cálculo

    availability = Column(Float, nullable=True)
    performance = Column(Float, nullable=True)
    quality = Column(Float, nullable=True)
    oee = Column(Float, nullable=True)

    planned_time_s = Column(Float, default=0)
    run_time_s = Column(Float, default=0)
    total_pieces = Column(Integer, default=0)
    good_pieces = Column(Integer, default=0)
    ideal_cycle_time_s = Column(Float, default=30)

    shift_label = Column(String(20), nullable=True)     # "T1", "T2", "T3"

    __table_args__ = (
        Index("ix_mes_oee_machine_ts", "machine_id", "ts"),
    )


class MachineStatus(Base):
    """Estado vivo actual de la máquina — una fila por machine_id."""
    __tablename__ = "mes_machine_status"

    machine_id = Column(String(50), primary_key=True)
    state = Column(String(30), nullable=False)
    last_event_ts = Column(DateTime, nullable=True)
    connected = Column(Boolean, default=True)
    piece_count = Column(Integer, default=0)
    good_count = Column(Integer, default=0)
    bad_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)
