import sys
import os

# Añadir el directorio backend al path de python
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(backend_dir)

from database.session import get_db
from sqlalchemy import text

def ver_eventos():
    with get_db() as db:
        # Consultar los últimos 50 eventos de JAULA-01
        query = text("""
            SELECT TOP 50 id, machine_id, state, timestamp, created_at, error, source 
            FROM dbo.mes_machine_events 
            WHERE machine_id = 'JAULA-01' 
            ORDER BY timestamp DESC, id DESC
        """)
        rows = db.execute(query).fetchall()
        print(f"{'ID':<6} | {'State':<15} | {'Timestamp':<28} | {'Created At':<28} | {'Source':<10} | {'Error'}")
        print("-" * 120)
        for r in rows:
            print(f"{r[0]:<6} | {r[2]:<15} | {str(r[3]):<28} | {str(r[4]):<28} | {r[6]:<10} | {r[5]}")

if __name__ == "__main__":
    ver_eventos()
