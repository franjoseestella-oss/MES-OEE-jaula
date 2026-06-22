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

# Get some sample rows from JAULA_ERP
cursor.execute("SELECT TOP 20 id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP ORDER BY id DESC")
rows = cursor.fetchall()
cols = [desc[0] for desc in cursor.description]

print("=== JAULA_ERP sample rows ===")
for row in rows:
    print({c: v for c, v in zip(cols, row)})

# Let's also check the distinct values of fecha_montaje to know what dates are present
cursor.execute("SELECT DISTINCT TOP 10 fecha_montaje FROM JAULA_ERP ORDER BY fecha_montaje DESC")
dates = cursor.fetchall()
print("\n=== Recent dates in JAULA_ERP ===")
for d in dates:
    print(d[0])
