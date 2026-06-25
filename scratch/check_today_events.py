import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("Events for today:")
cursor.execute("""
    SELECT timestamp, state, secuencia_id 
    FROM mes_machine_events 
    WHERE timestamp >= '2026-06-25 00:00:00' 
    ORDER BY timestamp ASC
""")
for r in cursor.fetchall():
    print(list(r))

conn.close()
