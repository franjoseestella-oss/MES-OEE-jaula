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

print("--- Sample of 10 rows from LOG_TABLA ---")
cursor.execute("""
    SELECT TOP 10 id, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, OK_NOK
    FROM LOG_TABLA
    ORDER BY id DESC
""")
for row in cursor.fetchall():
    print(f"id={row[0]} | FECHA_MONTAJE={row[1]} | FECHA_HORA_INICIO_SEC={row[2]} | OK_NOK={row[3]}")

print("\n--- Distinct FECHA_MONTAJE dates in LOG_TABLA ---")
cursor.execute("""
    SELECT DISTINCT CAST(FECHA_MONTAJE AS DATE)
    FROM LOG_TABLA
    ORDER BY 1 DESC
""")
for row in cursor.fetchall():
    print(row[0])

cursor.close()
conn.close()
