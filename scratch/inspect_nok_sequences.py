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

# Query LOG_TABLA for NOK
cursor.execute("SELECT TOP 20 id, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA WHERE OK_NOK = 'NOK' ORDER BY id DESC")
print("NOK logs in LOG_TABLA:")
for r in cursor.fetchall():
    print(r)

conn.close()
