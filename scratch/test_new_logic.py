import os
import sys
from dotenv import load_dotenv

# Add backend directory to path to use backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from config import get_settings
from sqlalchemy import create_engine, text

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
settings = get_settings()

engine = create_engine(settings.sqlalchemy_url)

setup_query = """
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());

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

-- Get completed sequences
IF OBJECT_ID('tempdb..#CompletedSeqs') IS NOT NULL DROP TABLE #CompletedSeqs;
CREATE TABLE #CompletedSeqs (
    id INT PRIMARY KEY,
    secuencia VARCHAR(50),
    bastidor VARCHAR(50),
    modelo VARCHAR(50),
    original_date DATE,
    actual_completion_date DATE,
    actual_start DATETIME,
    actual_end DATETIME,
    status VARCHAR(50),
    slot_idx_in_day INT
);

INSERT INTO #CompletedSeqs (id, secuencia, bastidor, modelo, original_date, actual_completion_date, actual_start, actual_end, status, slot_idx_in_day)
SELECT 
    id, secuencia, bastidor, modelo, original_date, actual_completion_date, actual_start, actual_end, status,
    ROW_NUMBER() OVER (PARTITION BY actual_completion_date ORDER BY actual_end ASC) AS slot_idx_in_day
FROM (
    SELECT 
        e.id,
        e.secuencia,
        e.bastidor,
        e.modelo,
        TRY_CAST(e.fecha_montaje AS DATE) AS original_date,
        CAST(l.FECHA_HORA_FIN_SEC AS DATE) AS actual_completion_date,
        TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AS actual_start,
        TRY_CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AS actual_end,
        COALESCE(l.OK_NOK, 'Pendiente') AS status
    FROM dbo.JAULA_ERP e
    INNER JOIN (
        SELECT 
            NBASTIDOR,
            OK_NOK,
            FECHA_HORA_INICIO_SEC,
            FECHA_HORA_FIN_SEC,
            ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
        FROM dbo.LOG_TABLA
        WHERE FECHA_HORA_FIN_SEC IS NOT NULL
    ) l ON l.NBASTIDOR = e.bastidor AND l.rn = 1
    WHERE TRY_CAST(e.secuencia AS INT) >= 227
) tmp;

DECLARE @MaxCompletionDate DATE;
SELECT @MaxCompletionDate = MAX(actual_completion_date) FROM #CompletedSeqs;
IF @MaxCompletionDate IS NULL SET @MaxCompletionDate = '2026-06-24';

DECLARE @CompletionsOnMaxDate INT;
SELECT @CompletionsOnMaxDate = COALESCE(MAX(slot_idx_in_day), 0) FROM #CompletedSeqs WHERE actual_completion_date = @MaxCompletionDate;

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

-- First insert completed sequences
INSERT INTO #MappedSeqs (id, secuencia, bastidor, modelo, original_date, planned_date, slot_idx, horario)
SELECT 
    id,
    secuencia,
    bastidor,
    modelo,
    original_date,
    actual_completion_date AS planned_date,
    slot_idx_in_day AS slot_idx,
    CAST(actual_end AS TIME) AS horario
FROM #CompletedSeqs;

-- Then insert pending sequences mapped to available slots
WITH AvailableSlots AS (
    SELECT 
        global_slot_idx,
        fecha,
        slot_idx_in_day,
        horario,
        ROW_NUMBER() OVER (ORDER BY fecha ASC, slot_idx_in_day ASC) AS available_slot_idx
    FROM #CalendarSlots
    WHERE fecha > @MaxCompletionDate
       OR (fecha = @MaxCompletionDate AND slot_idx_in_day > @CompletionsOnMaxDate)
),
OrderedPending AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as pending_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
      AND bastidor NOT IN (SELECT bastidor FROM #CompletedSeqs)
)
INSERT INTO #MappedSeqs (id, secuencia, bastidor, modelo, original_date, planned_date, slot_idx, horario)
SELECT 
    p.id,
    p.secuencia,
    p.bastidor,
    p.modelo,
    p.original_date,
    s.fecha AS planned_date,
    s.slot_idx_in_day AS slot_idx,
    s.horario
FROM OrderedPending p
LEFT JOIN AvailableSlots s ON s.available_slot_idx = p.pending_seq_idx;
"""

select_query = """
SELECT planned_date, COUNT(*) as count
FROM #MappedSeqs
GROUP BY planned_date
ORDER BY planned_date;
"""

with engine.connect() as conn:
    conn.execute(text(setup_query))
    result = conn.execute(text(select_query))
    columns = result.keys()
    rows = result.fetchall()
    print("Planned dates counts:")
    for row in rows:
        print(dict(zip(columns, row)))
