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

# Test various parsing logics
sql = """
SELECT 
    TRY_CONVERT(DATETIME, '29/6/2026 7:27:47', 103) AS conv_103,
    TRY_CONVERT(DATETIME, '29/6/2026, 7:27:47', 103) AS conv_with_comma
"""
cursor.execute(sql)
for r in cursor.fetchall():
    print(r)

conn.close()
