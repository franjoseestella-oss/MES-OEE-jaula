"""Tests de la lógica de cálculo OEE."""

import pytest
from datetime import datetime, timezone, timedelta
from oee.calculator import (
    OeeResult,
    EventRow,
    calculate_oee,
    oee_for_window,
)


def _ts(offset_s: float) -> datetime:
    base = datetime(2026, 6, 8, 6, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_s)


IDEAL_CYCLE = 30.0  # segundos por pieza
MACHINE = "MAQ-01"


def test_solo_execute():
    events = [
        EventRow(MACHINE, "Execute", _ts(0), piece_count=0,  good_count=0,  bad_count=0),
        EventRow(MACHINE, "Execute", _ts(60), piece_count=2, good_count=2, bad_count=0),
    ]
    result = calculate_oee(
        events=events,
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.availability == pytest.approx(1.0)
    assert result.run_time_s == pytest.approx(3600, rel=1e-3)


def test_execute_y_held():
    events = [
        EventRow(MACHINE, "Execute", _ts(0),    piece_count=0,   good_count=0,   bad_count=0),
        EventRow(MACHINE, "Held",    _ts(1800),  piece_count=60,  good_count=60,  bad_count=0),
        EventRow(MACHINE, "Execute", _ts(2700),  piece_count=60,  good_count=60,  bad_count=0),
    ]
    result = calculate_oee(
        events=events,
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.availability == pytest.approx(0.75, rel=0.01)
    assert result.run_time_s == pytest.approx(2700, rel=0.01)


def test_calidad_con_rechazos():
    events = [
        EventRow(MACHINE, "Execute", _ts(0),    piece_count=0,   good_count=0,   bad_count=0),
        EventRow(MACHINE, "Execute", _ts(3600),  piece_count=100, good_count=90,  bad_count=10),
    ]
    result = calculate_oee(
        events=events,
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.quality == pytest.approx(0.90, rel=0.01)
    assert result.total_pieces == 100
    assert result.good_pieces == 90


def test_sin_eventos():
    result = calculate_oee(
        events=[],
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.availability is None
    assert result.performance is None
    assert result.quality is None
    assert result.oee is None


def test_rendimiento_clipa_a_1():
    events = [
        EventRow(MACHINE, "Execute", _ts(0),    piece_count=0,   good_count=0,  bad_count=0),
        EventRow(MACHINE, "Execute", _ts(3600),  piece_count=200, good_count=200, bad_count=0),
    ]
    result = calculate_oee(
        events=events,
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.performance == pytest.approx(1.0)


def test_oee_completo():
    events = [
        EventRow(MACHINE, "Execute", _ts(0),    piece_count=0,   good_count=0,  bad_count=0),
        EventRow(MACHINE, "Held",    _ts(3000),  piece_count=90,  good_count=85, bad_count=5),
        EventRow(MACHINE, "Execute", _ts(3200),  piece_count=90,  good_count=85, bad_count=5),
        EventRow(MACHINE, "Execute", _ts(3600),  piece_count=92,  good_count=87, bad_count=5),
    ]
    result = calculate_oee(
        events=events,
        window_start=_ts(0),
        window_end=_ts(3600),
        ideal_cycle_time_s=IDEAL_CYCLE,
        machine_id=MACHINE,
        window_minutes=60,
    )
    assert result.availability is not None
    assert result.performance is not None
    assert result.quality is not None
    assert result.oee is not None
    assert 0 < result.oee <= 1.0
    assert result.oee == pytest.approx(
        result.availability * result.performance * result.quality, rel=1e-6
    )
