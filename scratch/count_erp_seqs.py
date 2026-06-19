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
SELECT fecha_montaje, COUNT(*)
FROM JAULA_ERP
WHERE fecha_montaje BETWEEN '20260615' AND '20260619'
GROUP BY fecha_montaje
ORDER BY fecha_montaje
""")
for r in cursor.fetchall():
    print(f"Date: {r[0]} Count: {r[1]}")
