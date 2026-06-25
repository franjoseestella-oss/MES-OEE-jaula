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
    print("Connection successful!")
    
    cursor.execute("SELECT TOP 5 id, NBASTIDOR, FECHA_MONTAJE, FECHA_HORA_FIN_SEC, OK_NOK FROM LOG_TABLA ORDER BY id DESC")
    rows = cursor.fetchall()
    print("LOG_TABLA Top 5:")
    for r in rows:
        print(f"id={r[0]}, NBASTIDOR={r[1]}, FECHA_MONTAJE={r[2]} (type: {type(r[2])}), FECHA_HORA_FIN_SEC={r[3]}, OK_NOK={r[4]}")
        
except Exception as e:
    print("Error:", e)
