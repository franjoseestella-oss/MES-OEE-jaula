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

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("--- DISTINCT fecha_montaje in JAULA_ERP ---")
    cursor.execute("SELECT DISTINCT fecha_montaje FROM JAULA_ERP ORDER BY fecha_montaje DESC")
    for row in cursor.fetchall():
        print(row[0])
        
    print("\n--- COUNT OF RECORDS IN JAULA_ERP FOR '20260612' ---")
    cursor.execute("SELECT COUNT(*) FROM JAULA_ERP WHERE fecha_montaje = '20260612'")
    print(cursor.fetchone()[0])
    
    print("\n--- COUNT OF RECORDS IN LOG_TABLA FOR '20260612' ---")
    cursor.execute("SELECT COUNT(*) FROM LOG_TABLA WHERE FECHA_MONTAJE = '20260612'")
    print(cursor.fetchone()[0])
    
    print("\n--- RECENT ENTRIES IN LOG_TABLA ---")
    cursor.execute("SELECT TOP 5 FECHA_MONTAJE, fecha_creacion, OK_NOK FROM LOG_TABLA ORDER BY id DESC")
    for row in cursor.fetchall():
        print(row)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
