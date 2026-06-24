import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # 1. Count matching rows first
    select_query = """
    SELECT COUNT(*) FROM LOG_TABLA
    WHERE FECHA_MONTAJE = '2026-06-24'
      AND OPERARIO = 'FORZADO NOK'
      AND OK_NOK = 'NOK'
    """
    cursor.execute(select_query)
    count = cursor.fetchone()[0]
    print(f"Found {count} forced NOK records for 24/06/2026.")
    
    if count > 0:
        # Show some of them
        show_query = """
        SELECT TOP 5 id, NSECUENCIA, NBASTIDOR, OK_NOK FROM LOG_TABLA
        WHERE FECHA_MONTAJE = '2026-06-24'
          AND OPERARIO = 'FORZADO NOK'
          AND OK_NOK = 'NOK'
        """
        cursor.execute(show_query)
        print("Sample records to delete:")
        for r in cursor.fetchall():
            print(r)
            
        # 2. Delete them
        delete_query = """
        DELETE FROM LOG_TABLA
        WHERE FECHA_MONTAJE = '2026-06-24'
          AND OPERARIO = 'FORZADO NOK'
          AND OK_NOK = 'NOK'
        """
        cursor.execute(delete_query)
        conn.commit()
        print(f"Successfully deleted {count} records from LOG_TABLA.")
    else:
        print("No records found to delete.")
        
    conn.close()

if __name__ == "__main__":
    main()
