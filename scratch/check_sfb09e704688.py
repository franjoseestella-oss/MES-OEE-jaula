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
    
    # Check LOG_TABLA
    cursor.execute("SELECT * FROM dbo.LOG_TABLA WHERE NBASTIDOR = 'SFB09E704688'")
    rows = cursor.fetchall()
    print("LOG_TABLA rows for SFB09E704688:")
    for r in rows:
        print(r)
        
    # Check REFERENCIA_EN_CICLO
    cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
    row = cursor.fetchone()
    print("\nREFERENCIA_EN_CICLO:")
    print(row)
    
except Exception as e:
    print("Error:", e)
