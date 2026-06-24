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

cursor.execute("SELECT TOP 5 timestamp, machine_id, state, secuencia_id FROM mes_machine_events ORDER BY timestamp DESC")
rows = cursor.fetchall()
colnames = [desc[0] for desc in cursor.description]
print("Columns:", colnames)
for row in rows:
    print(list(row))

cursor.close()
conn.close()
