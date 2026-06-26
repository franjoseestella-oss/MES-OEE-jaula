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

cursor.execute("""
    SELECT FECHA_MONTAJE, MIN(id), MAX(id), COUNT(*), MIN(NSECUENCIA), MAX(NSECUENCIA)
    FROM dbo.LOG_TABLA
    GROUP BY FECHA_MONTAJE
    ORDER BY FECHA_MONTAJE
""")
for r in cursor.fetchall():
    print(f"Log Date: {r[0]} | Min ID: {r[1]} | Max ID: {r[2]} | Count: {r[3]} | Min Seq: {r[4]} | Max Seq: {r[5]}")

cursor.close()
conn.close()
