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

# Get all sequences ordered by fecha_montaje
cursor.execute("""
SELECT 
    id,
    secuencia,
    bastidor,
    modelo,
    fecha_montaje
FROM dbo.JAULA_ERP
ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC
""")
rows = cursor.fetchall()

print("Chronological Order in JAULA_ERP:")
print("Index | ID | Secuencia | Bastidor | Modelo | Fecha Montaje")
print("-" * 75)
for idx, r in enumerate(rows):
    print(f"{idx+1:5d} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
    # Print first 30 and last 30
    if idx == 40:
        print("...")
    if idx > 40 and idx < len(rows) - 40:
        continue
    if idx >= len(rows) - 40:
        print(f"{idx+1:5d} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

cursor.close()
conn.close()
