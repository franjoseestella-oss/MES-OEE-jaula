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
    
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'REFERENCIA_EN_CICLO'")
    cols = cursor.fetchall()
    print("REFERENCIA_EN_CICLO columns:")
    for col in cols:
        print(col[0])
        
    cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
    rows = cursor.fetchall()
    print("REFERENCIA_EN_CICLO rows:")
    for r in rows:
        print(r)
        
except Exception as e:
    print("Error:", e)
