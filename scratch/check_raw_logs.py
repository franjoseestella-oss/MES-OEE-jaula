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

sql_query = """
SELECT TOP 10 
    NBASTIDOR, 
    FECHA_MONTAJE, 
    FECHA_HORA_INICIO_SEC, 
    FECHA_HORA_FIN_SEC, 
    OK_NOK
FROM dbo.LOG_TABLA
ORDER BY id DESC;
"""

try:
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    print("Logs:")
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)
conn.close()
