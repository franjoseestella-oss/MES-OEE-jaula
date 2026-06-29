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

cursor.execute("SELECT id, FECHA_Y_HORA, TIPO, DESCRIPCION, DURACION FROM dbo.LOG_ALARMAS ORDER BY id DESC")
for r in cursor.fetchall()[:25]:
    print(r)

conn.close()
