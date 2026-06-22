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

def main():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected successfully.")
        
        # Check some recent records
        cursor.execute("SELECT TOP 5 id, NSECUENCIA, OK_NOK FROM LOG_TABLA ORDER BY id DESC")
        rows = cursor.fetchall()
        print("Recent records:")
        for r in rows:
            print(f"id={r[0]}, NSECUENCIA={r[1]}, OK_NOK={r[2]}")
        
        if rows:
            test_id = rows[0][0]
            print(f"\nAttempting to update record id={test_id} to OK...")
            # We don't want to actually change it permanently if we are just testing, but let's see if update permission is granted
            # We will use a transaction and rollback
            conn.autocommit = False
            cursor.execute("UPDATE LOG_TABLA SET OK_NOK = 'OK' WHERE id = ?", (test_id,))
            print(f"Update executed. Rowcount = {cursor.rowcount}")
            conn.rollback()
            print("Transaction rolled back successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
