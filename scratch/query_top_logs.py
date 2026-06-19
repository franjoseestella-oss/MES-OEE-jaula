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

cursor.execute("SELECT COUNT(*) FROM LOG_TABLA")
total = cursor.fetchone()[0]
print(f"Total rows in LOG_TABLA: {total}")

cursor.execute("""
SELECT TOP 100 id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, FECHA_MONTAJE
FROM LOG_TABLA
ORDER BY id DESC
""")
rows = cursor.fetchall()
for r in rows:
    print(r)
