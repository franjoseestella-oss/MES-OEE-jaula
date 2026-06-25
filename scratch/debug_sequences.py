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

print("--- CALENDARIO_LABORAL ---")
cursor.execute("SELECT TOP 10 Fecha, Laborable, Cant_A_Fabricar, Tipo_Dia FROM dbo.CALENDARIO_LABORAL WHERE Fecha >= '2026-06-24' ORDER BY Fecha")
for r in cursor.fetchall():
    print(r)

print("\n--- JAULA_ERP ---")
cursor.execute("SELECT TOP 15 id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE TRY_CAST(secuencia AS INT) >= 227 ORDER BY TRY_CAST(secuencia AS INT)")
for r in cursor.fetchall():
    print(r)

print("\n--- LOG_TABLA recent ---")
cursor.execute("SELECT TOP 15 id, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA ORDER BY id DESC")
for r in cursor.fetchall():
    print(r)

conn.close()
