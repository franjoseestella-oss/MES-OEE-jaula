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

print("=== JAULA_ERP dates and counts ===")
cursor.execute("SELECT fecha_montaje, COUNT(*) FROM JAULA_ERP GROUP BY fecha_montaje ORDER BY fecha_montaje DESC")
for r in cursor.fetchall()[:10]:
    print(r)

print("\n=== LOG_TABLA dates and counts ===")
cursor.execute("SELECT CONVERT(varchar(10), FECHA_MONTAJE, 120), COUNT(*) FROM LOG_TABLA GROUP BY CONVERT(varchar(10), FECHA_MONTAJE, 120) ORDER BY CONVERT(varchar(10), FECHA_MONTAJE, 120) DESC")
for r in cursor.fetchall()[:10]:
    print(r)
