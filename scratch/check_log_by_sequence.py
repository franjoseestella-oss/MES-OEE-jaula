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
    
    query = "SELECT * FROM dbo.LOG_TABLA WHERE NSECUENCIA = 289"
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    print("Rows for sequence 289:")
    for r in rows:
        print(dict(zip(columns, r)))
        
except Exception as e:
    print("Error:", e)
