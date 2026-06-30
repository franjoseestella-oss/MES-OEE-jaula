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

cursor.execute("SELECT DISTINCT FECHA_MONTAJE FROM dbo.LOG_TABLA ORDER BY FECHA_MONTAJE DESC")
for r in cursor.fetchall():
    print(r)

print("\n--- Any entries with FECHA_HORA_INICIO_SEC? ---")
cursor.execute("SELECT TOP 5 id, NBASTIDOR, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, OK_NOK FROM dbo.LOG_TABLA WHERE FECHA_HORA_INICIO_SEC IS NOT NULL ORDER BY id DESC")
for r in cursor.fetchall():
    print(r)

conn.close()
