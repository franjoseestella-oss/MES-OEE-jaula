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

# Get all sequences in JAULA_ERP for 20260615
cursor.execute("""
SELECT id, secuencia, bastidor, modelo, fecha_montaje
FROM JAULA_ERP
WHERE fecha_montaje = '20260615'
ORDER BY id
""")
erp_rows = cursor.fetchall()
print("JAULA_ERP sequences for 20260615:")
for r in erp_rows:
    # check if this bastidor has any log
    cursor.execute("""
    SELECT id, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, FECHA_MONTAJE
    FROM LOG_TABLA
    WHERE NBASTIDOR = ?
    """, (r[2],))
    logs = cursor.fetchall()
    log_info = ", ".join([f"ID:{l[0]} Status:{l[1]} Start:{l[2]} End:{l[3]} MonDate:{l[4]}" for l in logs])
    print(f"ID: {r[0]} Seq: {r[1]} Bastidor: {r[2]} Model: {r[3]} Logs: [{log_info}]")
