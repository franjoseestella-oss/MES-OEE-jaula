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
    
    print("--- JAULA_ERP for '20260609' ---")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP WHERE fecha_montaje = '20260609' ORDER BY id")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- JAULA_ERP for '20260615' ---")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM JAULA_ERP WHERE fecha_montaje = '20260615' ORDER BY id")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- LOG_TABLA for '20260615' ---")
    cursor.execute("SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, fecha_creacion FROM LOG_TABLA WHERE FECHA_MONTAJE = '20260615' ORDER BY id")
    for row in cursor.fetchall():
        print(row)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
