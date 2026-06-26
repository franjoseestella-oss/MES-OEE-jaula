import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database.session import get_db

with get_db() as db:
    print("--- JAULA_ERP distinct fecha_montaje ---")
    try:
        res = db.execute(text("SELECT DISTINCT fecha_montaje FROM dbo.JAULA_ERP ORDER BY fecha_montaje DESC")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error JAULA_ERP:", e)

    print("\n--- LOG_TABLA distinct FECHA_MONTAJE ---")
    try:
        res = db.execute(text("SELECT DISTINCT FECHA_MONTAJE FROM dbo.LOG_TABLA ORDER BY FECHA_MONTAJE DESC")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error LOG_TABLA:", e)
