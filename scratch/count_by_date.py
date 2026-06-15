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
    
    print("--- JAULA_ERP Count by Date ---")
    cursor.execute("SELECT fecha_montaje, COUNT(*) FROM JAULA_ERP GROUP BY fecha_montaje ORDER BY fecha_montaje")
    for r in cursor.fetchall():
        print(r)
        
    print("\n--- LOG_TABLA Logs for today (2026-06-12) ---")
    cursor.execute("SELECT id, OPERARIO, FECHA_MONTAJE, NSECUENCIA, NBASTIDOR, OK_NOK, fecha_creacion FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = '2026-06-12' ORDER BY id")
    for r in cursor.fetchall():
        print(r)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
