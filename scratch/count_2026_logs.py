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

cursor.execute("""
    SELECT COUNT(*), MIN(FECHA_HORA_INICIO_SEC), MAX(FECHA_HORA_INICIO_SEC)
    FROM dbo.LOG_TABLA
    WHERE FECHA_HORA_INICIO_SEC LIKE '2026%'
""")
row = cursor.fetchone()
print(f"2026 log count: {row[0]} | Min: {row[1]} | Max: {row[2]}")

cursor.close()
conn.close()
