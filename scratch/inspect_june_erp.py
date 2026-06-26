import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database.session import get_db

with get_db() as db:
    print("--- June 2026 distinct JAULA_ERP fecha_montaje ---")
    try:
        res = db.execute(text("SELECT DISTINCT fecha_montaje FROM dbo.JAULA_ERP WHERE fecha_montaje LIKE '202606%' ORDER BY fecha_montaje DESC")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error JAULA_ERP:", e)
