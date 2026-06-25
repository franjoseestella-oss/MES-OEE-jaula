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
    
    cursor.execute("SELECT DISTINCT fecha_montaje FROM dbo.JAULA_ERP ORDER BY fecha_montaje DESC")
    rows = cursor.fetchall()
    print("Distinct fecha_montaje in JAULA_ERP:")
    for r in rows:
        print(r)
        
except Exception as e:
    print("Error:", e)
