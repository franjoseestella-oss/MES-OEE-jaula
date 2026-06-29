import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

query = """
DECLARE @ActiveDate VARCHAR(8) = '20260629';
DECLARE @PlotDate DATE = '2026-06-29';
DECLARE @SelectedDate DATE = '2026-06-29';

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStartDT DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @ShiftEndDT DATETIME = DATEADD(hour, 15 - @UTCOffset, CAST(@PlotDate AS DATETIME));

-- Current progress time limit
DECLARE @CurrentProgressTime DATETIME = GETUTCDATE();

-- Get active reference/sequence in cycle
DECLARE @ActiveBastidor VARCHAR(50);
DECLARE @ActiveStartDT DATETIME;

SELECT TOP 1 
    @ActiveBastidor = NBASTIDOR,
    @ActiveStartDT = DATEADD(hour, -@UTCOffset, TRY_CONVERT(DATETIME, 
        SUBSTRING(FECHA_INICIO_CICLO, 13, 4) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 10, 2) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 7, 2) + 'T' + 
        SUBSTRING(FECHA_INICIO_CICLO, 1, 5) + ':00'
    ))
FROM dbo.REFERENCIA_EN_CICLO
WHERE LEN(FECHA_INICIO_CICLO) >= 16;

-- Create schedule slots table
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

-- Map sequences starting from 227
IF OBJECT_ID('tempdb..#MappedSeqs') IS NOT NULL DROP TABLE #MappedSeqs;
CREATE TABLE #MappedSeqs (
    id INT PRIMARY KEY,
    secuencia VARCHAR(50),
    bastidor VARCHAR(50),
    modelo VARCHAR(50),
    original_date DATE,
    planned_date DATE,
    slot_idx INT,
    horario TIME
);

WITH OrderedERP AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
INSERT INTO #MappedSeqs (id, secuencia, bastidor, modelo, original_date, planned_date, slot_idx, horario)
SELECT 
    o.id,
    o.secuencia,
    o.bastidor,
    o.modelo,
    o.original_date,
    cs.fecha,
    cs.slot_idx_in_day,
    cs.horario
FROM OrderedERP o
LEFT JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

IF OBJECT_ID('tempdb..#SeqsToSchedule') IS NOT NULL DROP TABLE #SeqsToSchedule;
CREATE TABLE #SeqsToSchedule (
    id INT PRIMARY KEY,
    secuencia VARCHAR(50),
    bastidor VARCHAR(50),
    modelo VARCHAR(50),
    completed BIT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Pendiente',
    completion_time DATETIME,
    planned_start DATETIME,
    planned_end DATETIME,
    planned_date DATE,
    slot_idx INT,
    actual_start DATETIME,
    actual_end DATETIME
);

INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, modelo, completed, status, completion_time, planned_date, slot_idx, actual_start, actual_end)
SELECT 
    m.id,
    m.secuencia,
    m.bastidor,
    m.modelo,
    CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
    COALESCE(log.OK_NOK, 'Pendiente'),
    log.FECHA_HORA_FIN_SEC,
    m.planned_date,
    m.slot_idx,
    COALESCE(log.FECHA_HORA_INICIO_SEC, CASE WHEN m.bastidor = @ActiveBastidor THEN @ActiveStartDT ELSE NULL END),
    log.FECHA_HORA_FIN_SEC
FROM #MappedSeqs m
LEFT JOIN (
    SELECT 
        id,
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) AS FECHA_HORA_INICIO_SEC,
        TRY_CAST(FECHA_HORA_FIN_SEC AS DATETIME2) AS FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = m.bastidor AND log.rn = 1
WHERE m.planned_date = @SelectedDate;

SELECT secuencia, bastidor, planned_date, slot_idx, actual_start, actual_end FROM #SeqsToSchedule;
"""

cursor.execute(query)
while cursor.description is None:
    if not cursor.nextset():
        break

if cursor.description is not None:
    for r in cursor.fetchall():
        print(r)

conn.close()
