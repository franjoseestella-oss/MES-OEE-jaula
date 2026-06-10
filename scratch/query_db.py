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
SELECT 
  TIEMPO_ELEVACION_MEDIDO_SINCARGA AS [Elevación Sin Carga], 
  TIEMPO_ELEVACION_MIN_SINCARGA AS [Elevación Sin Carga Min], 
  TIEMPO_ELEVACION_MAX_SINCARGA AS [Elevación Sin Carga Max], 
  TIEMPO_DESCENSO_MEDIDO_SINCARGA AS [Descenso Sin Carga], 
  TIEMPO_DESCENSO_MIN_SINCARGA AS [Descenso Sin Carga Min], 
  TIEMPO_DESCENSO_MAX_SINCARGA AS [Descenso Sin Carga Max], 
  TIEMPO_ELEVACION_MEDIDO_CARGA AS [Elevación Con Carga], 
  TIEMPO_ELEVACION_MIN_CARGA AS [Elevación Con Carga Min], 
  TIEMPO_ELEVACION_MAX_CARGA AS [Elevación Con Carga Max], 
  TIEMPO_DESCENSO_MEDIDO_CARGA AS [Descenso Con Carga], 
  TIEMPO_DESCENSO_MIN_CARGA AS [Descenso Con Carga Min], 
  TIEMPO_DESCENSO_MAX_CARGA AS [Descenso Con Carga Max]
FROM LOG_TABLA 
WHERE id = 8
""")
row = cursor.fetchone()
cols = [desc[0] for desc in cursor.description]
for c, v in zip(cols, row):
    print(f"{c}: {v}")
