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
    
    print("--- 20260609 completion status ---")
    cursor.execute("""
        SELECT j.secuencia, j.bastidor, l.OK_NOK, l.fecha_creacion 
        FROM JAULA_ERP j 
        LEFT JOIN LOG_TABLA l ON j.bastidor = l.NBASTIDOR AND j.fecha_montaje = l.FECHA_MONTAJE
        WHERE j.fecha_montaje = '20260609'
    """)
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- 20260615 completion status ---")
    cursor.execute("""
        SELECT j.secuencia, j.bastidor, l.OK_NOK, l.fecha_creacion 
        FROM JAULA_ERP j 
        LEFT JOIN LOG_TABLA l ON j.bastidor = l.NBASTIDOR AND j.fecha_montaje = l.FECHA_MONTAJE
        WHERE j.fecha_montaje = '20260615'
    """)
    for row in cursor.fetchall():
        print(row)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
