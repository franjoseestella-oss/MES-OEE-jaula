import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database.session import get_db

with get_db() as db:
    print("--- TURNO_TRABAJO contents ---")
    try:
        res = db.execute(text("SELECT * FROM dbo.TURNO_TRABAJO")).mappings().all()
        for r in res:
            print(dict(r))
    except Exception as e:
        print("Error:", e)
