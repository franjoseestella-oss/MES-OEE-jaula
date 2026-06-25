import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = "SELECT TOP 10 id, OPERARIO, FECHA_MONTAJE, NSECUENCIA, NBASTIDOR, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, OK_NOK FROM dbo.LOG_TABLA ORDER BY id DESC"
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    print("Latest 10 logs in LOG_TABLA:")
    for r in rows:
        print(dict(zip(columns, r)))
        
except Exception as e:
    print("Error:", e)
