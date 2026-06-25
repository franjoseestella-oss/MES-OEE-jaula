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

cursor.execute("SELECT TOP 5 NSECUENCIA, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA ORDER BY id DESC")
for r in cursor.fetchall():
    print(list(r))

conn.close()
