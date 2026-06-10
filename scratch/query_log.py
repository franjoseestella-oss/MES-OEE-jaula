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

print("Connecting local to:", conn_str)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute(
    "SELECT TOP 10 id, "
    "TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA, "
    "fecha_creacion "
    "FROM LOG_TABLA ORDER BY id DESC"
)

rows = cursor.fetchall()
for r in rows:
    print(r)
conn.close()
