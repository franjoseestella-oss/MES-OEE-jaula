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
    
    cursor.execute("SELECT TOP 2 id, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM LOG_TABLA ORDER BY id DESC")
    rows = cursor.fetchall()
    for r in rows:
        print(f"id={r[0]}, INICIO={r[1]} (type: {type(r[1])}), FIN={r[2]} (type: {type(r[2])})")
        
except Exception as e:
    print("Error:", e)
