import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database.session import get_db
from database import repositories as repo
from models.events import OeeSnapshot

with get_db() as db:
    # Query last 10 snapshots
    snaps = db.query(OeeSnapshot).order_by(OeeSnapshot.ts.desc()).limit(10).all()
    print("=== PERSISTED SNAPSHOTS ===")
    for s in snaps:
        print(f"ID: {s.id} | Machine: {s.machine_id} | TS: {s.ts} | OEE: {s.oee} | A: {s.availability} | P: {s.performance} | Q: {s.quality} | Good/Total: {s.good_pieces}/{s.total_pieces} | Run/Planned: {s.run_time_s}/{s.planned_time_s} | Turno: {s.shift_label}")
