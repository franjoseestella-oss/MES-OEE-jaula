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
    rows = cursor.fetchall()
    print("Columns:", columns)
    print("Rows:")
    for r in rows:
        print(dict(zip(columns, r)))
except Exception as e:
    print("Error:", e)
