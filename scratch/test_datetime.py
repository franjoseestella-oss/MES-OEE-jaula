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

print("--- Testing FECHA_MONTAJE ---")
try:
    cursor.execute("""
        SELECT COUNT(*) FROM LOG_TABLA 
        WHERE FECHA_MONTAJE BETWEEN '2026-05-01T00:00:00Z' AND '2026-06-30T23:59:59Z'
    """)
    res = cursor.fetchone()[0]
    print(f"FECHA_MONTAJE count: {res}")
except Exception as e:
    print(f"FECHA_MONTAJE failed: {e}")

print("\n--- Testing FECHA_HORA_INICIO_SEC ---")
try:
    cursor.execute("""
        SELECT COUNT(*) FROM LOG_TABLA 
        WHERE FECHA_HORA_INICIO_SEC BETWEEN '2026-05-01T00:00:00Z' AND '2026-06-30T23:59:59Z'
    """)
    res = cursor.fetchone()[0]
    print(f"FECHA_HORA_INICIO_SEC count: {res}")
except Exception as e:
    print(f"FECHA_HORA_INICIO_SEC failed: {e}")

cursor.close()
conn.close()
