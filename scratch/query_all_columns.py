import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 * FROM LOG_TABLA ORDER BY fecha_creacion DESC")
row = cursor.fetchone()
columns = [column[0] for column in cursor.description]
for col, val in zip(columns, row):
    print(f"{col}: {val}")
