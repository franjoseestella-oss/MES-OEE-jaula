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
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("Checking id = 25:")
    cursor.execute("SELECT id, NSECUENCIA, OK_NOK FROM LOG_TABLA WHERE id = 25")
    row = cursor.fetchone()
    if row:
        print(f"Found row with id=25: id={row[0]}, NSECUENCIA={row[1]}, OK_NOK={row[2]}")
    else:
        print("No row with id=25 found.")
        
    print("\nChecking NSECUENCIA = 25:")
    cursor.execute("SELECT id, NSECUENCIA, OK_NOK FROM LOG_TABLA WHERE NSECUENCIA = 25")
    row = cursor.fetchone()
    if row:
        print(f"Found row with NSECUENCIA=25: id={row[0]}, NSECUENCIA={row[1]}, OK_NOK={row[2]}")
    else:
        print("No row with NSECUENCIA=25 found.")
        
    conn.close()

if __name__ == "__main__":
    main()
