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
    
    print("=== JAULA_ERP COLUMN NAMES ===")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'JAULA_ERP'")
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== SAMPLE JAULA_ERP RECORD ===")
    cursor.execute("SELECT TOP 5 * FROM JAULA_ERP")
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
