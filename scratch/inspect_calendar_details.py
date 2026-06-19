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

cursor.execute("SELECT TOP 0 * FROM dbo.CALENDARIO_LABORAL")
columns = [col[0] for col in cursor.description]
print(f"Columns: {columns}")

cursor.execute("SELECT TOP 10 * FROM dbo.CALENDARIO_LABORAL WHERE Laborable = 1")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
