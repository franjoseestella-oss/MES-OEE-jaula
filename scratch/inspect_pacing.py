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
    
    # Let's inspect the start sequencer logic for 20260608
    # 1. Min/Max/All rows of JAULA_ERP on 20260608
    print("--- JAULA_ERP rows on 20260608 ---")
    cursor.execute("""
        SELECT id, secuencia, bastidor, modelo,
               tpo_elevac_max, tpo_descenso_max, tpo_elev_max_scarga, tpo_desc_max_scarga
        FROM JAULA_ERP
        WHERE fecha_montaje = '20260608'
        ORDER BY id
    """)
    erp_rows = cursor.fetchall()
    for r in erp_rows:
        print(f"  id: {r[0]}, seq: {r[1]}, bastidor: {r[2]}, modelo: {r[3]}, cycle_times: {r[4]}/{r[5]}/{r[6]}/{r[7]}")
        
    # 2. LOG_TABLA rows on 20260608
    print("\n--- LOG_TABLA rows on 20260608 ---")
    cursor.execute("""
        SELECT id, NSECUENCIA, NBASTIDOR, NMODELO, OK_NOK, fecha_creacion, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC
        FROM LOG_TABLA
        WHERE FECHA_MONTAJE = '20260608'
        ORDER BY id
    """)
    log_rows = cursor.fetchall()
    for r in log_rows:
        print(f"  id: {r[0]}, seq: {r[1]}, bastidor: {r[2]}, model: {r[3]}, OK_NOK: {r[4]}, created: {r[5]}, start: {r[6]}, end: {r[7]}")

    # 3. Check Last_ERP_ID search for 20260608
    print("\n--- Start_Sec check for 20260608 ---")
    cursor.execute("""
        SELECT erp.id, erp.secuencia, erp.fecha_montaje, log.fecha_creacion, log.OK_NOK
        FROM JAULA_ERP erp
        INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
        WHERE log.fecha_creacion < '2026-06-08 07:00:00'
          AND log.OK_NOK = 'OK'
        ORDER BY erp.id DESC
    """)
    rows = cursor.fetchall()
    if rows:
        print(f"  Latest matching ERP ID before 07:00: {rows[0]}")
    else:
        print("  No matching ERP ID before 07:00")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
