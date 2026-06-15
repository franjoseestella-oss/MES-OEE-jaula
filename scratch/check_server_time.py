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
    cursor.execute("SELECT GETDATE() AS server_time, GETUTCDATE() AS utc_time")
    print("=== SERVER TIME ===")
    for r in cursor.fetchall():
        print(r)
    conn.close()

if __name__ == "__main__":
    inspect()
