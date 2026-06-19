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

cursor.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM LOG_TABLA")
count, min_id, max_id = cursor.fetchone()
print(f"Total rows: {count}, Min ID: {min_id}, Max ID: {max_id}")

cursor.execute("SELECT MIN(FECHA_MONTAJE), MAX(FECHA_MONTAJE) FROM LOG_TABLA")
min_fm, max_fm = cursor.fetchone()
print(f"FECHA_MONTAJE range: {min_fm} to {max_fm}")

cursor.execute("SELECT MIN(FECHA_HORA_INICIO_SEC), MAX(FECHA_HORA_INICIO_SEC) FROM LOG_TABLA")
min_fh, max_fh = cursor.fetchone()
print(f"FECHA_HORA_INICIO_SEC range: {min_fh} to {max_fh}")

cursor.close()
conn.close()
