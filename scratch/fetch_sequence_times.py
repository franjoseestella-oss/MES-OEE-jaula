import pyodbc
import sys

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

# Check active sequence in REFERENCIA_EN_CICLO
cursor.execute("SELECT NBASTIDOR, FECHA_INICIO_CICLO FROM dbo.REFERENCIA_EN_CICLO")
active = cursor.fetchall()
print("REFERENCIA_EN_CICLO:")
for r in active:
    print(f"  NBASTIDOR: {r[0]}, FECHA_INICIO_CICLO: {r[1]}")

# Check Log_tabla for 0261 (SFB09E704804)
cursor.execute("SELECT * FROM dbo.LOG_TABLA WHERE NBASTIDOR = 'SFB09E704804'")
log_rows = cursor.fetchall()
print("\nLOG_TABLA rows for SFB09E704804:")
for r in log_rows:
    print(r)

# Check JAULA_ERP for 0261 (SFB09E704804)
cursor.execute("SELECT * FROM dbo.JAULA_ERP WHERE bastidor = 'SFB09E704804'")
erp_rows = cursor.fetchall()
print("\nJAULA_ERP rows for SFB09E704804:")
for r in erp_rows:
    print(r)

conn.close()
