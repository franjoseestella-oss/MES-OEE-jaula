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

print("--- LATEST ALARMS IN LOG_ALARMAS ---")
cursor.execute("SELECT TOP 10 FECHA_Y_HORA, DURACION FROM dbo.LOG_ALARMAS ORDER BY id DESC")
for row in cursor.fetchall():
    print(row)

print("\n--- ACTIVE SEQUENCE IN REFERENCIA_EN_CICLO ---")
cursor.execute("SELECT TOP 5 NBASTIDOR, FECHA_INICIO_CICLO, OK_NOK FROM dbo.REFERENCIA_EN_CICLO")
for row in cursor.fetchall():
    print(row)

print("\n--- LATEST ENTRIES IN LOG_TABLA ---")
cursor.execute("SELECT TOP 5 id, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA ORDER BY id DESC")
for row in cursor.fetchall():
    print(row)

conn.close()
