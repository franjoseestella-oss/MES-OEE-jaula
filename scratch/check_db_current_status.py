import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("--- REFERENCIA_EN_CICLO ---")
    cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
    for r in cursor.fetchall():
        print(r)
        
    print("--- LOG_TABLA (top 10) ---")
    cursor.execute("SELECT TOP 10 * FROM dbo.LOG_TABLA ORDER BY id DESC")
    for r in cursor.fetchall():
        print(r)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
