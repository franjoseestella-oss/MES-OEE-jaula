import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "DATABASE=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("--- JAULA_ERP FOR 2026-06-29 ---")
    cursor.execute("""
        SELECT id, secuencia, bastidor, modelo, fecha_montaje
        FROM dbo.JAULA_ERP
        WHERE fecha_montaje = '2026-06-29' OR fecha_montaje = '20260629'
        ORDER BY id ASC
    """)
    for r in cursor.fetchall():
        print(r)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
