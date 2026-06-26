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

bastidors = ['SF14H-50253', 'SFB310703291', 'SF14H-00254', 'SFB08E704675', 'SFB08E704676']

print("=== Search by Bastidor ===")
for b in bastidors:
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor = ?", b)
    row = cursor.fetchone()
    if row:
        print(f"Bastidor: {b} -> Found in ERP: ID={row[0]}, Seq={row[1]}, Date={row[4]}")
    else:
        print(f"Bastidor: {b} -> NOT found in ERP")

print("\n=== Search by Seq (227-232) ===")
cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE TRY_CAST(secuencia AS INT) BETWEEN 227 AND 232 ORDER BY TRY_CAST(secuencia AS INT)")
for r in cursor.fetchall():
    print(f"Seq={r[1]}, Bastidor={r[2]}, Date={r[4]}")

cursor.close()
conn.close()
