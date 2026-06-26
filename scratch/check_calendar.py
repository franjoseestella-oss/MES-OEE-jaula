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

# Get details of CALENDARIO_LABORAL for June and July 2026
cursor.execute("""
SELECT Fecha, Laborable, Cant_A_Fabricar 
FROM dbo.CALENDARIO_LABORAL 
WHERE Fecha BETWEEN '2026-06-20' AND '2026-07-31'
ORDER BY Fecha ASC
""")
rows = cursor.fetchall()
print("Fecha | Laborable | Cant_A_Fabricar")
print("-" * 40)
for r in rows:
    print(f"{r[0]} | {r[1]} | {r[2]}")

cursor.close()
conn.close()
