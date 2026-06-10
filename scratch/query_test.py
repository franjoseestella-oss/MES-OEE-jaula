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

# Get the latest row
cursor.execute("SELECT TOP 1 id, fecha_creacion, OK_NOK, TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA FROM LOG_TABLA ORDER BY fecha_creacion DESC")
row = cursor.fetchone()
print("LATEST ROW:")
if row:
    print(f"id: {row.id}")
    print(f"fecha_creacion: {row.fecha_creacion}")
    print(f"OK_NOK: {row.OK_NOK}")
    print(f"TIEMPO_ELEVACION_MEDIDO_SINCARGA: {row.TIEMPO_ELEVACION_MEDIDO_SINCARGA}")
    print(f"TIEMPO_ELEVACION_MIN_SINCARGA: {row.TIEMPO_ELEVACION_MIN_SINCARGA}")
    print(f"TIEMPO_ELEVACION_MAX_SINCARGA: {row.TIEMPO_ELEVACION_MAX_SINCARGA}")

print("\nROW 12:")
cursor.execute("SELECT id, fecha_creacion, OK_NOK, TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA FROM LOG_TABLA WHERE id = 12")
row = cursor.fetchone()
if row:
    print(f"id: {row.id}")
    print(f"fecha_creacion: {row.fecha_creacion}")
    print(f"OK_NOK: {row.OK_NOK}")
    print(f"TIEMPO_ELEVACION_MEDIDO_SINCARGA: {row.TIEMPO_ELEVACION_MEDIDO_SINCARGA}")
    print(f"TIEMPO_ELEVACION_MIN_SINCARGA: {row.TIEMPO_ELEVACION_MIN_SINCARGA}")
    print(f"TIEMPO_ELEVACION_MAX_SINCARGA: {row.TIEMPO_ELEVACION_MAX_SINCARGA}")

conn.close()
