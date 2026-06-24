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

cursor.execute("SELECT COUNT(*) FROM dbo.JAULA_ERP WHERE fecha_montaje = '20260624'")
count = cursor.fetchone()[0]
print(f"Total sequences on 2026-06-24: {count}")

cursor.execute("SELECT secuencia, bastidor, modelo FROM dbo.JAULA_ERP WHERE fecha_montaje = '20260624' ORDER BY id")
rows = cursor.fetchall()
for i, r in enumerate(rows, 1):
    print(f"{i}: {list(r)}")

cursor.close()
conn.close()
