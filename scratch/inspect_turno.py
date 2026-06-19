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

cursor.execute("SELECT * FROM dbo.TURNO_TRABAJO")
rows = cursor.fetchall()
colnames = [desc[0] for desc in cursor.description]
print("Columns:", colnames)
for r in rows:
    print(r)

cursor.close()
conn.close()
