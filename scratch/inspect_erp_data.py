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
    
    print("=== JAULA_ERP ROW COUNT ===")
    cursor.execute("SELECT COUNT(*) FROM JAULA_ERP")
    print(f"Total rows: {cursor.fetchone()[0]}")
    
    print("\n=== DISTINCT FECHA_MONTAJE IN JAULA_ERP ===")
    cursor.execute("SELECT DISTINCT fecha_montaje FROM JAULA_ERP ORDER BY fecha_montaje")
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== SAMPLE ROWS AROUND 2026-06-24 IN JAULA_ERP ===")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP WHERE fecha_montaje IN ('20260623', '20260624', '20260625') ORDER BY fecha_montaje, Try_cast(secuencia as int)")
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
