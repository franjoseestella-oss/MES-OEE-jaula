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
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE fecha_montaje = '20260624' ORDER BY TRY_CAST(secuencia AS INT) ASC")
    rows = cursor.fetchall()
    print("June 24 sequences in ERP:")
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    inspect()
