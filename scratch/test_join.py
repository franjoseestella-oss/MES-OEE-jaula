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
    
    print("=== TESTING JOIN BY NSECUENCIA ===")
    cursor.execute("""
        SELECT TOP 10 erp.secuencia, erp.bastidor, log.id, log.NSECUENCIA, log.NBASTIDOR, log.FECHA_MONTAJE
        FROM JAULA_ERP erp
        INNER JOIN LOG_TABLA log ON log.NSECUENCIA = TRY_CAST(erp.secuencia AS FLOAT)
        ORDER BY erp.id DESC
    """)
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
