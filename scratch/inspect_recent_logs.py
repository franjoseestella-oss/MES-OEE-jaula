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
    
    print("=== LOG_TABLA LAST 30 ENTRIES ===")
    cursor.execute("""
        SELECT TOP 30 id, NSECUENCIA, NBASTIDOR, NMODELO, FECHA_MONTAJE, OK_NOK, FECHA_HORA_FIN_SEC 
        FROM LOG_TABLA 
        ORDER BY id DESC
    """)
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
