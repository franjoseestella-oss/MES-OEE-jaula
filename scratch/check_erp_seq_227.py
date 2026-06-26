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

# Find ERP rows with sequence like 227
cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE secuencia LIKE '%227%' OR secuencia = '0227' OR secuencia = '227'")
rows = cursor.fetchall()
print("=== ERP ROWS for 227 ===")
for r in rows:
    print(f"ERP ID: {r[0]} | Seq: {r[1]} | Bastidor: {r[2]} | Modelo: {r[3]} | Fecha: {r[4]}")

cursor.close()
conn.close()
