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
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE TRY_CAST(secuencia AS INT) BETWEEN 227 AND 300 ORDER BY TRY_CAST(secuencia AS INT) ASC, fecha_montaje ASC")
    rows = cursor.fetchall()
    print("Sequences 227-300 in ERP:")
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    inspect()
