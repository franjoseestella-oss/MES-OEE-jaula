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
    
    cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    
    print("Columns and values:")
    print("-" * 50)
    for col, val in zip(columns, row):
        print(f"{col}: {val} (type: {type(val)})")
        
except Exception as e:
    print("Error:", e)
