import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Find the unique fecha_montaje values in JAULA_ERP for June 2026
cursor.execute("""
    SELECT DISTINCT fecha_montaje 
    FROM dbo.JAULA_ERP 
    WHERE fecha_montaje LIKE '202606%' 
    ORDER BY fecha_montaje
""")
dates = [r[0] for r in cursor.fetchall()]
print(f"Dates in June 2026: {dates}")

# Let's inspect the sequences for some dates, including id ranges and count
for d in dates[:5]:
    cursor.execute(f"SELECT MIN(id), MAX(id), COUNT(*), MIN(secuencia), MAX(secuencia) FROM dbo.JAULA_ERP WHERE fecha_montaje = '{d}'")
    row = cursor.fetchone()
    print(f"Date: {d} | Min ID: {row[0]} | Max ID: {row[1]} | Count: {row[2]} | Min Seq: {row[3]} | Max Seq: {row[4]}")

cursor.close()
conn.close()
