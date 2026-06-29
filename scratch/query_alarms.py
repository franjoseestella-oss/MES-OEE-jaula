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

cursor.execute("""
    SELECT id, DESCRIPCION, FECHA_Y_HORA, DURACION 
    FROM dbo.LOG_ALARMAS
    WHERE DESCRIPCION LIKE '%ALARMA CR%'
    ORDER BY id DESC
""")
print("Critical alarms in LOG_ALARMAS:")
for r in cursor.fetchall():
    print(r)

conn.close()
