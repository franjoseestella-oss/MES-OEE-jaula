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
    
    print("=== LOG_TABLA FOR 2026-06-24 ===")
    cursor.execute("""
        SELECT id, NSECUENCIA, NBASTIDOR, NMODELO, FECHA_MONTAJE, OK_NOK, FECHA_HORA_FIN_SEC
        FROM LOG_TABLA 
        WHERE CAST(FECHA_MONTAJE AS DATE) = '2026-06-24'
        ORDER BY id ASC
    """)
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
