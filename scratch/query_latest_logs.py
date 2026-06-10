import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT TOP 5 id, fecha_creacion, TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA, TIEMPO_DESCENSO_MEDIDO_SINCARGA, TIEMPO_DESCENSO_MIN_SINCARGA, TIEMPO_DESCENSO_MAX_SINCARGA FROM LOG_TABLA ORDER BY fecha_creacion DESC")
rows = cursor.fetchall()
for r in rows:
    print(r)
