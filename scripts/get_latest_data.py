import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

SERVER   = r"DESKTOP-PMRMSPT\SQLEXPRESS"
DATABASE = "DAFEED"
TABLE    = "dbo.LOG_TABLA"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str, timeout=10)
cursor = conn.cursor()

# Get the latest row columns
cursor.execute(f"SELECT TOP 1 * FROM {TABLE} ORDER BY fecha_creacion DESC")
row = cursor.fetchone()
if row:
    col_names = [desc[0] for desc in cursor.description]
    for name, val in zip(col_names, row):
        if 'TIEMPO' in name or 'ELEVACION' in name or 'DESCENSO' in name or 'OK_NOK' in name:
            print(f"{name}: {val}")
else:
    print("No rows found")
conn.close()
