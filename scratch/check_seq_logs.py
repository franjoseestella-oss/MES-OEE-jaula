import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

for seq in [130, 134, 135, 136, 137]:
    cursor.execute("""
    SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_MONTAJE
    FROM LOG_TABLA
    WHERE NSECUENCIA = ?
    """, (seq,))
    rows = cursor.fetchall()
    print(f"Logs for sequence {seq}:")
    for r in rows:
        print(r)
