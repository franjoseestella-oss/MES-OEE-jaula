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

# 1. Total rows in both tables
cursor.execute("SELECT COUNT(*) FROM dbo.JAULA_ERP")
erp_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM dbo.LOG_TABLA")
log_count = cursor.fetchone()[0]
print(f"Total in JAULA_ERP: {erp_count}, Total in LOG_TABLA: {log_count}")

# 2. Match by exact bastidor
cursor.execute("SELECT COUNT(DISTINCT erp.bastidor) FROM dbo.JAULA_ERP erp INNER JOIN dbo.LOG_TABLA log ON log.NBASTIDOR = erp.bastidor")
match_exact = cursor.fetchone()[0]
print(f"Unique matching bastidors: {match_exact}")

# Let's see some example bastidors in LOG_TABLA and see if we can find them in JAULA_ERP
cursor.execute("SELECT TOP 20 NBASTIDOR, NSECUENCIA, FECHA_MONTAJE FROM dbo.LOG_TABLA ORDER BY id DESC")
rows = cursor.fetchall()
print("\n=== Recent logs and their existence in ERP ===")
for r in rows:
    cursor.execute("SELECT COUNT(*) FROM dbo.JAULA_ERP WHERE bastidor = ?", r[0])
    count = cursor.fetchone()[0]
    print(f"Log Bastidor: {r[0]} | Seq: {r[1]} | Date: {r[2]} | Matches in ERP: {count}")
    if count == 0:
        # Search for substring
        sub = r[0][-5:] if len(r[0]) >= 5 else r[0]
        cursor.execute("SELECT bastidor, secuencia, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor LIKE ?", f"%{sub}%")
        matches = cursor.fetchall()
        if matches:
            print(f"   -> Substring match for '{sub}': {matches[:3]}")

cursor.close()
conn.close()
