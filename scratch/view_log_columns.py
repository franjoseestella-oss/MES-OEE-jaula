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

print("=== LOG_TABLA columns ===")
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'LOG_TABLA'")
for r in cursor.fetchall():
    print(r)

print("\n=== LOG_TABLA count ===")
cursor.execute("SELECT COUNT(*) FROM LOG_TABLA")
print("Total rows:", cursor.fetchone()[0])

print("\n=== LOG_TABLA last 5 rows ===")
cursor.execute("SELECT TOP 5 id, OPERARIO, FECHA_MONTAJE, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM LOG_TABLA ORDER BY id DESC")
for r in cursor.fetchall():
    print(r)

conn.close()
