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

cursor.execute("SELECT MIN(fecha_montaje), MAX(fecha_montaje), COUNT(*) FROM JAULA_ERP")
row = cursor.fetchone()
print(f"JAULA_ERP range: Min={row[0]} Max={row[1]} Total={row[2]}")

cursor.execute("SELECT COUNT(*) FROM JAULA_ERP WHERE fecha_montaje < '20260615'")
count_before = cursor.fetchone()[0]
print(f"Rows before 2026-06-15: {count_before}")
