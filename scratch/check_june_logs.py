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

cursor.execute("SELECT id, NBASTIDOR, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, OK_NOK FROM dbo.LOG_TABLA WHERE FECHA_MONTAJE >= '2026-06-01' ORDER BY id ASC")
for r in cursor.fetchall():
    print(r)

conn.close()
