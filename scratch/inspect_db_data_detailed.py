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
    
    print("=== RECENT LOG_TABLA RECORDS ===")
    cursor.execute("SELECT TOP 10 id, fecha_creacion, FECHA_MONTAJE, NSECUENCIA, NBASTIDOR, OK_NOK FROM LOG_TABLA ORDER BY id DESC")
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== JAULA_ERP FOR 20260615 ===")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP WHERE fecha_montaje = '20260615' ORDER BY id ASC")
    for r in cursor.fetchall():
        print(r)

    print("\n=== JAULA_ERP FOR 20260609 ===")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP WHERE fecha_montaje = '20260609' ORDER BY id ASC")
    for r in cursor.fetchall():
        print(r)

    conn.close()

if __name__ == "__main__":
    inspect()
