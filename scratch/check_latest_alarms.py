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

cursor.execute("SELECT * FROM dbo.LOG_ALARMAS ORDER BY id DESC")
columns = [column[0] for column in cursor.description]
print("Columns:", columns)
for r in cursor.fetchall()[:20]:
    print(r)

conn.close()
