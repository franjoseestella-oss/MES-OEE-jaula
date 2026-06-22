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

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting: {e}")
    sys.exit(1)

cursor.execute("SELECT GETDATE(), CAST(GETDATE() AS DATE)")
row = cursor.fetchone()
print(f"GETDATE(): {row[0]}, CAST AS DATE: {row[1]}")

cursor.execute("SELECT TOP 5 FECHA_MONTAJE, FECHA_HORA_INICIO_SEC FROM LOG_TABLA ORDER BY id DESC")
print("Latest rows in LOG_TABLA:")
for r in cursor.fetchall():
    print(f"FECHA_MONTAJE: {r[0]}, FECHA_HORA_INICIO_SEC: {r[1]}")

conn.close()
