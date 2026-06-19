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

cursor.execute("""
    SELECT id, NSECUENCIA, NBASTIDOR, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, OK_NOK 
    FROM dbo.LOG_TABLA 
    WHERE FECHA_HORA_INICIO_SEC LIKE '2026%'
    ORDER BY id ASC
""")
for r in cursor.fetchall():
    print(r)

cursor.close()
conn.close()
