import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("Checking LOG_TABLA for 24/06/2026:")
cursor.execute("SELECT * FROM dbo.LOG_TABLA WHERE FECHA_MONTAJE = '2026-06-24'")
rows = cursor.fetchall()
print(f"Total rows in LOG_TABLA: {len(rows)}")
for r in rows[:10]:
    print(r)

print("\nChecking mes_machine_events for today:")
cursor.execute("SELECT DISTINCT secuencia_id, state, timestamp FROM mes_machine_events ORDER BY timestamp DESC")
events = cursor.fetchall()
print(f"Total events: {len(events)}")
for e in events[:10]:
    print(e)

cursor.close()
conn.close()
