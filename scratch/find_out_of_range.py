import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute(
    "SELECT id, "
    "TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA, "
    "TIEMPO_DESCENSO_MEDIDO_SINCARGA, TIEMPO_DESCENSO_MIN_SINCARGA, TIEMPO_DESCENSO_MAX_SINCARGA "
    "FROM LOG_TABLA "
    "ORDER BY fecha_creacion DESC"
)

rows = cursor.fetchall()
for r in rows:
    id_val = r[0]
    elev_med = r[1]
    elev_min = r[2]
    elev_max = r[3]
    desc_med = r[4]
    desc_min = r[5]
    desc_max = r[6]
    
    out_of_range = []
    if elev_med is not None and elev_min is not None and elev_max is not None:
        if not (elev_min <= elev_med <= elev_max):
            out_of_range.append(f"Elevacion Sin Carga: med={elev_med}, min={elev_min}, max={elev_max}")
    if desc_med is not None and desc_min is not None and desc_max is not None:
        if not (desc_min <= desc_med <= desc_max):
            out_of_range.append(f"Descenso Sin Carga: med={desc_med}, min={desc_min}, max={desc_max}")
            
    if out_of_range:
        print(f"Record ID: {id_val}")
        for err in out_of_range:
            print(f"  {err}")
conn.close()
