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
    
    print("=== LOG_TABLA COLUMN NAMES AND TYPES ===")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'LOG_TABLA'")
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== SAMPLE DATA ===")
    cursor.execute("SELECT TOP 3 FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, fecha_creacion FROM LOG_TABLA ORDER BY id DESC")
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    main()
