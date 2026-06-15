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
    cursor.execute("SELECT * FROM LOG_TABLA WHERE id BETWEEN 30 AND 40 ORDER BY id ASC")
    print("=== LOG_TABLA BETWEEN 30 AND 40 ===")
    for r in cursor.fetchall():
        print(r)
    conn.close()

if __name__ == "__main__":
    inspect()
