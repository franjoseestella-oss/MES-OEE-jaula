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
    
    print("--- TABLES ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    for r in cursor.fetchall():
        print(r[0])
        
    print("\n--- REFERENCIA_EN_CICLO columns ---")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'REFERENCIA_EN_CICLO'")
    for r in cursor.fetchall():
        print(r)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
