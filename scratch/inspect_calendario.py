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
    
    print("=== CALENDARIO_LABORAL COLUMN NAMES ===")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CALENDARIO_LABORAL'")
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== RECENT CALENDARIO_LABORAL ENTRIES ===")
    cursor.execute("SELECT TOP 20 * FROM CALENDARIO_LABORAL WHERE fecha >= '2026-06-01' ORDER BY fecha ASC")
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
