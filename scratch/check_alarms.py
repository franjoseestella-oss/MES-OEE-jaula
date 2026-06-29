import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

query = """
SELECT id, FECHA_Y_HORA, DESCRIPCION, DURACION
FROM dbo.LOG_ALARMAS
ORDER BY id DESC;
"""
cursor.execute(query)
print("LOG_ALARMAS ROWS:")
for r in cursor.fetchall()[:30]:
    print(r)

conn.close()
