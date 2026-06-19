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
cursor.execute("SELECT id, fecha_montaje, secuencia, bastidor, modelo FROM dbo.JAULA_ERP WHERE bastidor = 'SF13H-50001'")
print("JAULA_ERP rows:")
for r in cursor.fetchall():
    print(r)

# Query LOG_TABLA
cursor.execute("SELECT * FROM dbo.LOG_TABLA WHERE NBASTIDOR = 'SF13H-50001'")
print("\nLOG_TABLA rows:")
for r in cursor.fetchall():
    print(r)

conn.close()
