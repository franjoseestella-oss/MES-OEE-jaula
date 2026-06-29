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
    
    print("--- MACHINE EVENTS WITH SECUENCIA_ID ON 2026-06-29 ---")
    cursor.execute("""
        SELECT id, state, timestamp, secuencia_id, piece_count, good_count, bad_count
        FROM dbo.mes_machine_events
        WHERE secuencia_id IS NOT NULL AND CAST(timestamp AS DATE) = '2026-06-29'
        ORDER BY id ASC
    """)
    for r in cursor.fetchall():
        print(r)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
