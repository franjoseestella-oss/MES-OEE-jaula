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

# Get Calendar laborable days starting from '2026-06-24'
cursor.execute("""
SELECT Fecha, Laborable, Cant_A_Fabricar 
FROM dbo.CALENDARIO_LABORAL 
WHERE Fecha >= '2026-06-24' AND Laborable = 1 AND Cant_A_Fabricar > 0
ORDER BY Fecha ASC
""")
cal_days = cursor.fetchall()

# Get ERP counts per day
cursor.execute("""
SELECT fecha_montaje, COUNT(*) 
FROM dbo.JAULA_ERP 
GROUP BY fecha_montaje
""")
erp_counts = {row[0]: row[1] for row in cursor.fetchall()}

print("Date | Laborable | Cant_A_Fabricar (Slots) | ERP Seq Count")
print("-" * 60)
for day in cal_days:
    d_str = day[0].strftime("%Y%m%d")
    erp_cnt = erp_counts.get(d_str, 0)
    print(f"{day[0]} | {day[1]} | {day[2]} | {erp_cnt}")

cursor.close()
conn.close()
