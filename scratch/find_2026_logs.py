import pyodbc

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
SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, FECHA_MONTAJE
FROM LOG_TABLA
WHERE FECHA_HORA_INICIO_SEC LIKE '2026%' OR FECHA_MONTAJE LIKE '2026%'
ORDER BY id
""")
rows = cursor.fetchall()
print(f"Found {len(rows)} logs from 2026:")
for r in rows:
    print(r)
