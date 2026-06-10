import pyodbc

SERVER   = r"DESKTOP-PMRMSPT\SQLEXPRESS"
DATABASE = "DAFEED"
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        id,
        TIEMPO_ELEVACION_MEDIDO_SINCARGA,
        TIEMPO_ELEVACION_MIN_SINCARGA,
        TIEMPO_ELEVACION_MAX_SINCARGA,
        TIEMPO_DESCENSO_MEDIDO_SINCARGA,
        TIEMPO_DESCENSO_MIN_SINCARGA,
        TIEMPO_DESCENSO_MAX_SINCARGA,
        TIEMPO_ELEVACION_MEDIDO_CARGA,
        TIEMPO_ELEVACION_MIN_CARGA,
        TIEMPO_ELEVACION_MAX_CARGA,
        TIEMPO_DESCENSO_MEDIDO_CARGA,
        TIEMPO_DESCENSO_MIN_CARGA,
        TIEMPO_DESCENSO_MAX_CARGA
    FROM LOG_TABLA 
    WHERE id = 31
""")

row = cursor.fetchone()
columns = [col[0] for col in cursor.description]
data = dict(zip(columns, row))

import json
print(json.dumps(data, indent=2))
