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

print("Searching for similar to SF18F-50264 or 50264...")
cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor LIKE '%50264%' OR bastidor LIKE '%SF18F%'")
for r in cursor.fetchall()[:10]:
    print(r)

print("\nSearching for similar to SFB09E704690 or 704690...")
cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor LIKE '%704690%' OR bastidor LIKE '%SFB09E%'")
for r in cursor.fetchall()[:10]:
    print(r)

cursor.close()
conn.close()
