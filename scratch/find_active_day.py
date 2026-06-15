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
    
    print("--- JAULA_ERP counts in June 2026 ---")
    cursor.execute("""
        SELECT fecha_montaje, COUNT(*) 
        FROM JAULA_ERP 
        WHERE fecha_montaje LIKE '202606%' 
        GROUP BY fecha_montaje 
        ORDER BY fecha_montaje DESC
    """)
    for row in cursor.fetchall():
        print(f"  fecha_montaje: {row[0]}, count: {row[1]}")
        
    print("\n--- LOG_TABLA counts in June 2026 ---")
    cursor.execute("""
        SELECT FECHA_MONTAJE, COUNT(*) 
        FROM LOG_TABLA 
        WHERE FECHA_MONTAJE LIKE '202606%' 
        GROUP BY FECHA_MONTAJE 
        ORDER BY FECHA_MONTAJE DESC
    """)
    for row in cursor.fetchall():
        print(f"  FECHA_MONTAJE: {row[0]}, count: {row[1]}")
        
    # Let's find the latest date in LOG_TABLA and show matches for that date
    cursor.execute("SELECT MAX(FECHA_MONTAJE) FROM LOG_TABLA")
    latest_log_date = cursor.fetchone()[0]
    print(f"\nLatest date in LOG_TABLA: {latest_log_date}")
    
    if latest_log_date:
        print(f"\n--- Matches for date {latest_log_date} ---")
        cursor.execute(f"""
            SELECT 
                j.secuencia, j.bastidor, j.modelo,
                l.NSECUENCIA, l.NBASTIDOR, l.OK_NOK
            FROM JAULA_ERP j
            LEFT JOIN LOG_TABLA l ON j.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = '{latest_log_date}'
            WHERE j.fecha_montaje = '{latest_log_date}'
            ORDER BY CAST(j.secuencia AS INT)
        """)
        rows = cursor.fetchall()
        print(f"Total planned on {latest_log_date}: {len(rows)}")
        matched = sum(1 for r in rows if r[4] is not None)
        print(f"Matched/Realized: {matched}")
        for r in rows[:15]:
            print(f"  Seq: {r[0]} | Bastidor: {r[1]} | Modelo: {r[2]} -> Realized Seq: {r[3]} | OK_NOK: {r[5]}")

except Exception as e:
    print(f"Error: {e}")
