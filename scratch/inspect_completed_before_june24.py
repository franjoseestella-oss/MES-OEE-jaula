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

# Find the last completed sequence before June 24
query = """
SELECT TOP 20 log.id, log.NSECUENCIA, log.NBASTIDOR, log.OK_NOK, log.FECHA_MONTAJE, log.FECHA_HORA_INICIO_SEC, log.FECHA_HORA_FIN_SEC
FROM dbo.LOG_TABLA log
WHERE log.OK_NOK = 'OK' AND YEAR(log.FECHA_MONTAJE) = 2026
ORDER BY log.id DESC
"""

cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    print(r)

cursor.close()
conn.close()
