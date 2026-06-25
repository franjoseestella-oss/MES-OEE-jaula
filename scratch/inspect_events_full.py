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
    cursor.execute("SELECT TOP 20 * FROM dbo.mes_machine_events ORDER BY id DESC")
    columns = [d[0] for d in cursor.description]
    print("Columns:", columns)
    rows = cursor.fetchall()
    for r in rows:
        print(dict(zip(columns, r)))
    conn.close()

if __name__ == "__main__":
    inspect()
