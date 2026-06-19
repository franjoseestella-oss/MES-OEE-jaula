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

# Test 1: Count rows using FECHA_MONTAJE filter for 2026-06-15 to 2026-06-17
print("--- Filtering by FECHA_MONTAJE ('2026-06-15' to '2026-06-17') ---")
cursor.execute("""
    SELECT COUNT(*) FROM LOG_TABLA 
    WHERE FECHA_MONTAJE >= '2026-06-15' AND FECHA_MONTAJE < '2026-06-18'
""")
print("Count:", cursor.fetchone()[0])

# Test 2: Count rows using FECHA_HORA_INICIO_SEC filter for 2026-06-15 to 2026-06-17
print("\n--- Filtering by FECHA_HORA_INICIO_SEC ('2026-06-15' to '2026-06-17') ---")
cursor.execute("""
    SELECT COUNT(*), MIN(FECHA_HORA_INICIO_SEC), MAX(FECHA_HORA_INICIO_SEC)
    FROM LOG_TABLA 
    WHERE FECHA_HORA_INICIO_SEC >= '2026-06-15' AND FECHA_HORA_INICIO_SEC < '2026-06-18'
""")
res = cursor.fetchone()
print("Count:", res[0], "Min:", res[1], "Max:", res[2])

cursor.close()
conn.close()
