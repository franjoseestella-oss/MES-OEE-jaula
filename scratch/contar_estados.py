import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database.session import get_db
from sqlalchemy import text

with get_db() as db:
    rows = db.execute(text("SELECT state, COUNT(*) FROM dbo.mes_machine_events WHERE machine_id='JAULA-01' GROUP BY state")).fetchall()
    print("=== EVENT COUNT BY STATE ===")
    for r in rows:
        print(f"State: {r[0]} | Count: {r[1]}")
