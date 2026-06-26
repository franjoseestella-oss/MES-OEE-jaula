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

# Get slots per day
# Map sequences within each day
cursor.execute("""
WITH CalendarSlots AS (
    SELECT 
        cb.Fecha,
        s.seq_idx,
        s.horario
    FROM dbo.CALENDARIO_LABORAL cb
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
        WHERE cb.Cant_A_Fabricar = 18.5 AND id BETWEEN 1 AND 19 -- simplification for check
    ) s
    WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
),
OrderedERP AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (PARTITION BY fecha_montaje ORDER BY TRY_CAST(secuencia AS INT) ASC) as slot_idx_in_day
    FROM dbo.JAULA_ERP
)
SELECT 
    o.secuencia,
    o.bastidor,
    o.original_date,
    cs.Fecha as mapped_date,
    o.slot_idx_in_day,
    cs.horario
FROM OrderedERP o
LEFT JOIN CalendarSlots cs ON cs.Fecha = o.original_date AND cs.seq_idx = o.slot_idx_in_day
ORDER BY o.original_date ASC, o.slot_idx_in_day ASC
""")
rows = cursor.fetchall()

print("Seq | Bastidor | ERP Original Fecha | Mapped Fecha | Slot in Day | Mapped Hora")
print("-" * 80)
for idx, r in enumerate(rows):
    # Print sample rows from June and July
    if idx < 10 or (idx > 15 and idx < 25) or idx > len(rows) - 10:
        print(f"{r[0]} | {r[1]:12s} | {r[2]} | {r[3]} | {r[4]:11d} | {r[5]}")
    elif idx == 10 or idx == 25:
        print("...")

cursor.close()
conn.close()
