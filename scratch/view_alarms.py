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

print("--- LOG_ALARMAS ---")
cursor.execute("SELECT TOP 50 * FROM dbo.LOG_ALARMAS ORDER BY FECHA_Y_HORA DESC")
for r in cursor.fetchall():
    print(r)

conn.close()
