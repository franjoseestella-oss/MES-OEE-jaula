import pyodbc
import sys

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
    
    print("=== JAULA_ERP columns ===")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'JAULA_ERP'")
    for r in cursor.fetchall():
        print(r)

    print("\n=== JAULA_ERP sample rows (top 5) ===")
    cursor.execute("SELECT TOP 5 * FROM JAULA_ERP ORDER BY id DESC")
    cols = [col[0] for col in cursor.description]
    for r in cursor.fetchall():
        print(dict(zip(cols, r)))
        
    conn.close()

if __name__ == "__main__":
    main()
