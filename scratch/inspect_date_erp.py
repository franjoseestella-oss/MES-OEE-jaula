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
SELECT DISTINCT fecha_montaje
FROM JAULA_ERP
WHERE fecha_montaje BETWEEN '20260610' AND '20260625'
ORDER BY fecha_montaje
""")
rows = cursor.fetchall()
print("Dates in JAULA_ERP:")
for r in rows:
    print(r[0])

cursor.execute("""
SELECT TOP 5 * FROM JAULA_ERP WHERE fecha_montaje = '20260615' ORDER BY id
""")
rows = cursor.fetchall()
print("\nFirst 5 rows for 20260615:")
for r in rows:
    print(r)
