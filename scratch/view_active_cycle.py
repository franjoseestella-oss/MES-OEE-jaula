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

print("--- REFERENCIA_EN_CICLO ---")
cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
for r in cursor.fetchall():
    print(r)

print("\n--- RECENT LOG_TABLA ---")
cursor.execute("SELECT TOP 5 * FROM dbo.LOG_TABLA ORDER BY id DESC")
for r in cursor.fetchall():
    print(r)

conn.close()
