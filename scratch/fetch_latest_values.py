import pyodbc
from dotenv import dotenv_values

config = dotenv_values(".env")

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={config['SQL_SERVER_HOST']},{config['SQL_SERVER_PORT']};"
    f"DATABASE={config['SQL_SERVER_DATABASE']};"
    f"UID={config['SQL_SERVER_USER']};"
    f"PWD={config['SQL_SERVER_PASSWORD']};"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute(
    "SELECT TOP 1 "
    "id, fecha_creacion, "
    "TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA, "
    "TIEMPO_DESCENSO_MEDIDO_SINCARGA, TIEMPO_DESCENSO_MIN_SINCARGA, TIEMPO_DESCENSO_MAX_SINCARGA, "
    "TIEMPO_ELEVACION_MEDIDO_CARGA, TIEMPO_ELEVACION_MIN_CARGA, TIEMPO_ELEVACION_MAX_CARGA, "
    "TIEMPO_DESCENSO_MEDIDO_CARGA, TIEMPO_DESCENSO_MIN_CARGA, TIEMPO_DESCENSO_MAX_CARGA "
    "FROM LOG_TABLA ORDER BY id DESC"
)

row = cursor.fetchone()
cols = [desc[0] for desc in cursor.description]
for col, val in zip(cols, row):
    print(f"{col}: {val}")
conn.close()
