import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

query = """
SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC
FROM dbo.LOG_TABLA
WHERE FECHA_MONTAJE = '20260624'
   OR FECHA_HORA_INICIO_SEC LIKE '2026-06-24%'
   OR FECHA_HORA_INICIO_SEC LIKE '2026-06-25%'
ORDER BY id DESC
"""

cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    print(r)

cursor.close()
conn.close()
