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
    
    # 1. Check unique dates in JAULA_ERP
    print("--- Dates in JAULA_ERP ---")
    cursor.execute("SELECT DISTINCT TOP 10 fecha_montaje FROM JAULA_ERP ORDER BY fecha_montaje DESC")
    for row in cursor.fetchall():
        print(f"  fecha_montaje: {row[0]}")
        
    # 2. Check unique dates in LOG_TABLA
    print("\n--- Dates in LOG_TABLA ---")
    cursor.execute("SELECT DISTINCT TOP 10 FECHA_MONTAJE FROM LOG_TABLA ORDER BY FECHA_MONTAJE DESC")
    for row in cursor.fetchall():
        print(f"  FECHA_MONTAJE: {row[0]}")
        
    # 3. Check sample match between JAULA_ERP and LOG_TABLA for a recent date (e.g. today or latest date)
    print("\n--- Sample data match by bastidor/sequence ---")
    cursor.execute("""
        SELECT TOP 10 
            j.fecha_montaje, j.secuencia, j.bastidor, j.modelo,
            l.NSECUENCIA, l.NBASTIDOR, l.OK_NOK
        FROM JAULA_ERP j
        LEFT JOIN LOG_TABLA l ON j.bastidor = l.NBASTIDOR
        ORDER BY j.fecha_montaje DESC
    """)
    for row in cursor.fetchall():
        print(f"  ERP: {row[0]}/{row[1]}/{row[2]} ({row[3]}) -> LOG: {row[4]}/{row[5]} [{row[6]}]")

except Exception as e:
    print(f"Error: {e}")
