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

print("--- ALL ALARMS FOR 2026-06-29 OR RELATED ---")
cursor.execute("SELECT * FROM dbo.LOG_ALARMAS ORDER BY id DESC")
columns = [col[0] for col in cursor.description]
for r in cursor.fetchall()[:30]:
    row_dict = dict(zip(columns, r))
    print(f"ID: {row_dict['id']}, FECHA: {row_dict['FECHA_Y_HORA']}, DESC: {row_dict['DESCRIPCION']}, DURACION: {row_dict['DURACION']}")

conn.close()
