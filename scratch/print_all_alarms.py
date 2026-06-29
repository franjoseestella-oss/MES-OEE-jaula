import pyodbc

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS;DATABASE=DAFEED;UID=usuario_readonly;PWD=Logisnext2026!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT * FROM dbo.LOG_ALARMAS ORDER BY ID DESC")
rows = cursor.fetchall()
for idx, r in enumerate(rows):
    print(f"Row {idx}: ID={r[0]}, FECHA_Y_HORA={repr(r[1])}, TIPO={repr(r[2])}, TEXTO={repr(r[3])}, DURACION={repr(r[4])}")
conn.close()
