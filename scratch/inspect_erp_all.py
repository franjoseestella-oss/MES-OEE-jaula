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

# Find the unique fecha_montaje values in JAULA_ERP
cursor.execute("""
    SELECT fecha_montaje, MIN(id), MAX(id), COUNT(*), MIN(secuencia), MAX(secuencia)
    FROM dbo.JAULA_ERP
    GROUP BY fecha_montaje
    ORDER BY fecha_montaje
""")
for r in cursor.fetchall():
    print(f"Date: {r[0]} | Min ID: {r[1]} | Max ID: {r[2]} | Count: {r[3]} | Min Seq: {r[4]} | Max Seq: {r[5]}")

cursor.close()
conn.close()
