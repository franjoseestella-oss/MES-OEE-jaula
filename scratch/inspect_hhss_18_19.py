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

print("--- HHSS_18 ---")
cursor.execute("SELECT TOP 5 * FROM dbo.HHSS_18")
print([col[0] for col in cursor.description])
cursor.execute("SELECT COUNT(*) FROM dbo.HHSS_18")
print(f"Total rows: {cursor.fetchone()[0]}")

print("--- HHSS_19 ---")
cursor.execute("SELECT TOP 5 * FROM dbo.HHSS_19")
print([col[0] for col in cursor.description])
cursor.execute("SELECT COUNT(*) FROM dbo.HHSS_19")
print(f"Total rows: {cursor.fetchone()[0]}")

cursor.close()
conn.close()
