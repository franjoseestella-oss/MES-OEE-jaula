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

cursor.execute("""
SELECT 
    id,
    secuencia,
    bastidor,
    modelo,
    fecha_montaje
FROM dbo.JAULA_ERP
ORDER BY TRY_CAST(secuencia AS INT) ASC
""")
rows = cursor.fetchall()

print("ID | Secuencia | Bastidor | Modelo | Fecha Montaje")
print("-" * 60)
for r in rows:
    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

cursor.close()
conn.close()
