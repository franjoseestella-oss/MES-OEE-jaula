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

# Query JAULA_ERP
cursor.execute("SELECT id, fecha_montaje, secuencia, bastidor, modelo FROM dbo.JAULA_ERP WHERE bastidor = 'STB310703243'")
print("JAULA_ERP rows:")
for r in cursor.fetchall():
    print(r)

# Query LOG_TABLA
cursor.execute("SELECT id, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA WHERE NBASTIDOR = 'STB310703243'")
print("\nLOG_TABLA rows:")
for r in cursor.fetchall():
    print(r)

conn.close()
