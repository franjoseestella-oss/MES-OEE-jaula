import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, OPERARIO, FECHA_MONTAJE, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC 
    FROM dbo.LOG_TABLA 
    WHERE NSECUENCIA IN (273, 274) 
    ORDER BY id
""")
rows = cursor.fetchall()
print("=== LOG_TABLA ROWS for sequence 273/274 ===")
for r in rows:
    print(f"Log ID: {r[0]} | Operario: {r[1]} | Fecha Montaje: {r[2]} | Seq: {r[3]} | Bastidor: {r[4]} | OK/NOK: {r[5]} | Start: {r[6]} | End: {r[7]}")

cursor.close()
conn.close()
