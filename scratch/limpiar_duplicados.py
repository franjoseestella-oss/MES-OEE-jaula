import sys
import os

# Añadir el directorio backend al path de python
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(backend_dir)

from database.session import get_db
from sqlalchemy import text

def limpiar_duplicados():
    with get_db() as db:
        # Primero ver cuántos duplicados hay
        query_count = text("""
            SELECT machine_id, timestamp, COUNT(*) as cnt
            FROM dbo.mes_machine_events
            GROUP BY machine_id, timestamp
            HAVING COUNT(*) > 1
        """)
        dupes = db.execute(query_count).fetchall()
        print(f"Parejas/grupos con duplicados detectados: {len(dupes)}")
        
        if len(dupes) > 0:
            # Ejecutar la eliminación
            query_delete = text("""
                WITH CTE AS (
                    SELECT id,
                           ROW_NUMBER() OVER (PARTITION BY machine_id, timestamp ORDER BY id ASC) as rn
                    FROM dbo.mes_machine_events
                )
                DELETE FROM dbo.mes_machine_events
                WHERE id IN (SELECT id FROM CTE WHERE rn > 1)
            """)
            result = db.execute(query_delete)
            print(f"Duplicados eliminados. Filas afectadas: {result.rowcount}")
        else:
            print("No hay eventos duplicados en la base de datos.")

if __name__ == "__main__":
    limpiar_duplicados()
