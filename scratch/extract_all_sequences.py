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
    
    # Query all sequences for the month of June 2026
    cursor.execute("""
        SELECT 
            j.fecha_montaje,
            j.secuencia,
            j.bastidor,
            j.modelo,
            l.NSECUENCIA,
            l.NBASTIDOR,
            l.OK_NOK,
            l.fecha_creacion
        FROM JAULA_ERP j
        LEFT JOIN LOG_TABLA l ON j.bastidor = l.NBASTIDOR
        WHERE j.fecha_montaje LIKE '202606%'
        ORDER BY j.fecha_montaje DESC, CAST(j.secuencia AS INT) ASC
    """)
    
    rows = cursor.fetchall()
    print(f"Total rows queried: {len(rows)}")
    
    # Group by date
    data_by_date = {}
    for r in rows:
        f_montaje = r[0]
        if f_montaje not in data_by_date:
            data_by_date[f_montaje] = []
        data_by_date[f_montaje].append({
            'secuencia_erp': r[1],
            'bastidor_erp': r[2],
            'modelo_erp': r[3],
            'realizada': r[4] is not None,
            'secuencia_log': r[4],
            'ok_nok': r[6],
            'fecha_creacion': r[7]
        })
        
    for date, seqs in sorted(data_by_date.items(), reverse=True):
        realized_count = sum(1 for s in seqs if s['realizada'])
        print(f"\nFecha: {date} (Planificadas: {len(seqs)}, Realizadas: {realized_count})")
        for s in seqs:
            status_str = "PENDIENTE"
            if s['realizada']:
                status_str = f"REALIZADA ({s['ok_nok']})"
            print(f"  Seq ERP: {s['secuencia_erp']} | Bastidor: {s['bastidor_erp']} | Modelo: {s['modelo_erp']} -> {status_str}")

except Exception as e:
    print(f"Error: {e}")
