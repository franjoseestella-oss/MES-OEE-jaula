import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

def inspect():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha_creacion, fecha_montaje, nsecuencia, ok_nok FROM LOG_TABLA ORDER BY id ASC")
    print("=== ALL LOGS IN LOG_TABLA ===")
    for r in cursor.fetchall():
        print(r)
    conn.close()

if __name__ == "__main__":
    inspect()
