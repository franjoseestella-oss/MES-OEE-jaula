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

# Get the count of sequences per date in ERP
cursor.execute("""
SELECT TRY_CAST(fecha_montaje AS DATE) AS original_date, COUNT(*) as cnt
FROM dbo.JAULA_ERP
GROUP BY TRY_CAST(fecha_montaje AS DATE)
ORDER BY original_date ASC
""")
erp_counts = cursor.fetchall()
print("ERP Counts per date:")
for r in erp_counts:
    print(f"  Date: {r[0]} | Count: {r[1]}")

# Old global mapping vs new partitioned mapping for a few sequences
cursor.execute("""
SET NOCOUNT ON;
IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
CREATE TABLE #CalendarSlots (
    global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE,
    slot_idx_in_day INT,
    horario TIME
);

WITH CalendarBase AS (
    SELECT 
        Fecha,
        Laborable,
        Cant_A_Fabricar,
        SUM(CASE WHEN Cant_A_Fabricar = 18.5 THEN 1 ELSE 0 END) OVER (ORDER BY Fecha ASC) AS Count185
    FROM dbo.CALENDARIO_LABORAL
    WHERE Fecha >= '2026-06-24'
)
INSERT INTO #CalendarSlots (fecha, slot_idx_in_day, horario)
SELECT 
    cb.Fecha,
    s.seq_idx,
    s.horario
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
ORDER BY cb.Fecha ASC, s.seq_idx ASC;

-- Global mapped
WITH OrderedERP AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
SELECT 
    o.secuencia, o.bastidor, o.original_date, cs.fecha AS global_mapped_date
INTO #GlobalMapped
FROM OrderedERP o
LEFT JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

-- Partitioned mapped
WITH OrderedERP2 AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (PARTITION BY fecha_montaje ORDER BY TRY_CAST(secuencia AS INT) ASC) as slot_idx_in_day
    FROM dbo.JAULA_ERP
)
SELECT 
    o.secuencia, o.bastidor, o.original_date, o.original_date AS part_mapped_date
INTO #PartMapped
FROM OrderedERP2 o;

SELECT TOP 20
    g.secuencia,
    g.bastidor,
    g.original_date,
    g.global_mapped_date,
    p.part_mapped_date
FROM #GlobalMapped g
INNER JOIN #PartMapped p ON p.secuencia = g.secuencia AND p.bastidor = g.bastidor
ORDER BY g.original_date ASC, g.secuencia ASC;
""")

rows = cursor.fetchall()
print("\nComparison:")
print("Seq | Bastidor | ERP Original | Global Mapped | Partition Mapped")
print("-" * 80)
for r in rows:
    print(f"{r[0]} | {r[1]:12s} | {r[2]} | {r[3]} | {r[4]}")

cursor.close()
conn.close()
