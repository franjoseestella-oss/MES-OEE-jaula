import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, OK_NOK, NBASTIDOR, NMODELO
    FROM LOG_TABLA 
    WHERE FECHA_MONTAJE >= '2026-06-01'
    ORDER BY id DESC
""")
for row in cursor.fetchall():
    print(f"id={row[0]} | FECHA_MONTAJE={row[1]} | FECHA_HORA_INICIO_SEC={row[2]} | OK_NOK={row[3]} | BASTIDOR={row[4]} | MODELO={row[5]}")

cursor.close()
conn.close()
