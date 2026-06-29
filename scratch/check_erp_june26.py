import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE fecha_montaje = '20260626'")
rows = cursor.fetchall()
print(f"Total rows on 2026-06-26: {len(rows)}")
for r in rows:
    print(r)

conn.close()
