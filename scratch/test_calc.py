import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database.session import get_db
from database import repositories as repo
from oee.calculator import oee_for_window, EventRow
from config import get_settings

def test_calculo():
    settings = get_settings()
    now = datetime.now(timezone.utc)
    window_minutes = 60
    since = now - timedelta(minutes=window_minutes)
    
    with get_db() as db:
        events_db = repo.get_events_in_range(db, "JAULA-01", since, now)
        print(f"Eventos en la última hora: {len(events_db)}")
        
        events = []
        for ev in events_db:
            ts = ev.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            events.append(EventRow(
                machine_id=ev.machine_id,
                state=ev.state,
                timestamp=ts,
                piece_count=ev.piece_count or 0,
                good_count=ev.good_count or 0,
                bad_count=ev.bad_count or 0,
            ))
            print(f"  - Event: {ev.state} @ {ts}")
            
        result = oee_for_window(
            events=events,
            machine_id="JAULA-01",
            minutes=window_minutes,
            ideal_cycle_time_s=settings.ideal_cycle_time_seconds,
            reference_ts=now,
        )
        print(f"=== RESULTADO DEL CÁLCULO ===")
        print(f"Planned time: {result.planned_time_s}s")
        print(f"Run time: {result.run_time_s}s")
        print(f"Availability: {result.availability}")
        print(f"OEE: {result.oee}")

if __name__ == "__main__":
    test_calculo()
