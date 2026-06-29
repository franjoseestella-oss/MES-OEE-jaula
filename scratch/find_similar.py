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

cursor.execute("SELECT TOP 100 id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE TRY_CAST(secuencia AS INT) BETWEEN 227 AND 292 ORDER BY secuencia ASC")
for r in cursor.fetchall():
    print(r)

conn.close()
