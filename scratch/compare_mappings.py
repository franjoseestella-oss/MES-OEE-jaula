import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get Calendar slots starting from '2026-06-24'
cursor.execute("""
WITH CalendarBase AS (
    SELECT 
        Fecha,
        Laborable,
        Cant_A_Fabricar,
        SUM(CASE WHEN Cant_A_Fabricar = 18.5 THEN 1 ELSE 0 END) OVER (ORDER BY Fecha ASC) AS Count185
    FROM dbo.CALENDARIO_LABORAL
    WHERE Fecha >= '2026-06-24'
)
SELECT 
    cb.Fecha,
    s.seq_idx,
    s.horario,
    ROW_NUMBER() OVER (ORDER BY cb.Fecha ASC, s.seq_idx ASC) as global_slot_idx
FROM CalendarBase cb
CROSS APPLY (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx, horario
    FROM dbo.HHSS_18
    WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx, horario
    FROM dbo.HHSS_19
    WHERE cb.Cant_A_Fabricar = 19.0
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx, horario
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 1 AND id BETWEEN 1 AND 19
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx, horario
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 0 AND id BETWEEN 20 AND 38
) s
WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
ORDER BY cb.Fecha ASC, s.seq_idx ASC
""")
slots = cursor.fetchall()
slots_dict = {row[3]: (row[0], row[1], row[2]) for row in slots}

# Get Ordered ERP sequences
cursor.execute("""
SELECT 
    id,
    secuencia,
    bastidor,
    modelo,
    fecha_montaje
FROM dbo.JAULA_ERP
WHERE TRY_CAST(secuencia AS INT) >= 227
ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC
""")
erp_rows = cursor.fetchall()

print("Global Slot Index | Seq | Bastidor | ERP Original Fecha | Mapped Fecha | Mapped Slot | Mapped Hora")
print("-" * 100)
for idx, row in enumerate(erp_rows):
    global_seq_idx = idx + 1
    mapped = slots_dict.get(global_seq_idx, (None, None, None))
    print(f"{global_seq_idx:17d} | {row[1]} | {row[2]:12s} | {row[4]} | {str(mapped[0])} | {str(mapped[1])} | {str(mapped[2])}")
    if idx > 60:
        break

cursor.close()
conn.close()
