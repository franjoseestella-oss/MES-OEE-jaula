import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

# Get total row count, distinct dates, distinct sequence ranges
cursor.execute("SELECT COUNT(*) FROM dbo.JAULA_ERP")
total_rows = cursor.fetchone()[0]

cursor.execute("SELECT MIN(fecha_montaje), MAX(fecha_montaje) FROM dbo.JAULA_ERP")
min_date, max_date = cursor.fetchone()

cursor.execute("SELECT MIN(TRY_CAST(secuencia AS INT)), MAX(TRY_CAST(secuencia AS INT)) FROM dbo.JAULA_ERP")
min_seq, max_seq = cursor.fetchone()

print(f"Total Rows: {total_rows}")
print(f"Date Range in JAULA_ERP: {min_date} to {max_date}")
print(f"Sequence Range: {min_seq} to {max_seq}")

# Let's see the distinct assembly dates and count of sequences per date
cursor.execute("""
SELECT 
    fecha_montaje,
    COUNT(*),
    MIN(TRY_CAST(secuencia AS INT)),
    MAX(TRY_CAST(secuencia AS INT))
FROM dbo.JAULA_ERP
GROUP BY fecha_montaje
ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC
""")
dates = cursor.fetchall()
print("\nDate | Count | Min Seq | Max Seq")
print("-" * 40)
for d in dates:
    print(f"{d[0]} | {d[1]:5d} | {d[2]:7d} | {d[3]:7d}")

cursor.close()
conn.close()
