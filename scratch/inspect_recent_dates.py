import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database.session import get_db

with get_db() as db:
    print("--- Top 20 distinct JAULA_ERP fecha_montaje DESC ---")
    try:
        res = db.execute(text("SELECT DISTINCT TOP 20 fecha_montaje FROM dbo.JAULA_ERP ORDER BY fecha_montaje DESC")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error JAULA_ERP:", e)

    print("\n--- Top 20 distinct LOG_TABLA FECHA_MONTAJE DESC ---")
    try:
        res = db.execute(text("SELECT DISTINCT TOP 20 FECHA_MONTAJE FROM dbo.LOG_TABLA ORDER BY FECHA_MONTAJE DESC")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error LOG_TABLA:", e)
