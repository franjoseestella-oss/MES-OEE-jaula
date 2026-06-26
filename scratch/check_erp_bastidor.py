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

# Find ERP rows with bastidor like SF14H-50253
cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor LIKE '%SF14H-50253%' OR bastidor LIKE '%50253%'")
rows = cursor.fetchall()
print("=== ERP ROWS for bastidor ===")
for r in rows:
    print(f"ERP ID: {r[0]} | Seq: {r[1]} | Bastidor: {r[2]} | Modelo: {r[3]} | Fecha: {r[4]}")

cursor.close()
conn.close()
