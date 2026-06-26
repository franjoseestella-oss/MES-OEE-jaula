import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor = 'SF18F-50264'")
r = cursor.fetchone()
if r:
    print(f"Found in ERP: ID: {r[0]} | Seq: {r[1]} | Bastidor: {r[2]} | Modelo: {r[3]} | Fecha: {r[4]}")
else:
    print("Not found in ERP!")

cursor.close()
conn.close()
