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

cursor.execute("SELECT COUNT(*) FROM mes_oee_snapshots WHERE oee IS NOT NULL")
non_null_oee_count = cursor.fetchone()[0]
print(f"Rows with non-null oee: {non_null_oee_count}")

cursor.execute("SELECT TOP 5 * FROM mes_oee_snapshots WHERE oee IS NOT NULL ORDER BY ts DESC")
columns = [column[0] for column in cursor.description]
for row in cursor.fetchall():
    print(dict(zip(columns, row)))
