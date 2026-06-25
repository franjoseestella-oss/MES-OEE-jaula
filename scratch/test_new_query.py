import pyodbc
import sys

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

active_date_val = "20260625"

test_sql = f"""
SET NOCOUNT ON;
DECLARE @ActiveDate VARCHAR(8) = '{active_date_val}';
DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = TRY_CAST(@ActiveDate AS DATE);

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStartDT DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @ShiftEndDT DATETIME = DATEADD(hour, 15 - @UTCOffset, CAST(@PlotDate AS DATETIME));

-- Current progress time limit
DECLARE @CurrentProgressTime DATETIME;
SELECT @CurrentProgressTime = CASE 
    WHEN CAST(GETDATE() AS DATE) = @PlotDate THEN GETUTCDATE()
    WHEN @PlotDate > CAST(GETDATE() AS DATE) THEN @ShiftStartDT
    ELSE @ShiftEndDT
END;

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
    slot_idx INT
);

INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, modelo, completed, status, completion_time, planned_date, slot_idx)
SELECT 
    m.id,
    m.secuencia,
    m.bastidor,
    m.modelo,
    CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
    COALESCE(log.OK_NOK, 'Pendiente'),
    log.FECHA_HORA_FIN_SEC,
    m.planned_date,
    m.slot_idx
FROM #MappedSeqs m
LEFT JOIN (
    SELECT 
        id,
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = m.bastidor AND log.rn = 1
WHERE 
    -- Show sequences planned for the selected day
    (m.planned_date = @SelectedDate)
    -- OR sequences planned for the past that are pending (not completed, or completed today)
    OR (
        (m.planned_date < @SelectedDate OR m.planned_date IS NULL)
        AND (
            log.id IS NULL 
            OR log.OK_NOK = 'NOK' 
            OR CAST(log.FECHA_MONTAJE AS DATE) = @SelectedDate
        )
    );

UPDATE s
SET 
    s.planned_start = DATEADD(hour, -@UTCOffset, DATEADD(second, 
        CASE 
            WHEN m.slot_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
    )),
    s.planned_end = DATEADD(hour, -@UTCOffset, CASE 
        WHEN m.horario IS NOT NULL THEN 
            DATEADD(second, 
                DATEDIFF(second, '07:00:00', m.horario),
                DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
            )
        ELSE
            DATEADD(minute, 25, 
                DATEADD(second, 
                    CASE 
                        WHEN m.slot_idx = 1 THEN 0
                        ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                    END,
                    DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
                )
            )
    END)
FROM #SeqsToSchedule s
INNER JOIN #MappedSeqs m ON m.id = s.id
LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = m.planned_date AND t_prev.slot_idx_in_day = m.slot_idx - 1;

-- Output for timeline
WITH SequenceStates AS (
    SELECT 
        secuencia,
        bastidor,
        planned_start,
        planned_end,
        planned_date,
        slot_idx,
        (
            SELECT TOP 1 state 
            FROM mes_machine_events 
            WHERE secuencia_id = s.secuencia 
            ORDER BY timestamp DESC
        ) AS latest_state
    FROM #SeqsToSchedule s
)
SELECT time, metric, value FROM (
    -- Shift start boundary to force horizontal axis range
    SELECT 
        @ShiftStartDT AS time,
        CONCAT(secuencia, CHAR(10), bastidor) AS metric,
        NULL AS value,
        planned_date,
        slot_idx,
        1 AS sort_time_order
    FROM SequenceStates
    
    UNION ALL
    
    -- Sequence planned start with its state (capped at shift boundaries and current progress)
    SELECT 
        CASE 
            WHEN planned_start < @ShiftStartDT THEN @ShiftStartDT 
            WHEN planned_start > @ShiftEndDT THEN @ShiftEndDT
            ELSE planned_start 
        END AS time,
        CONCAT(secuencia, CHAR(10), bastidor) AS metric,
        CASE 
            WHEN planned_start > @CurrentProgressTime THEN NULL
            ELSE CASE COALESCE(latest_state, 'Idle')
                WHEN 'Execute' THEN 'En proceso'
                WHEN 'Starting' THEN 'Secuencia iniciada'
                WHEN 'Running' THEN 'En proceso'
                WHEN 'Idle' THEN 'Esperando máquina'
                WHEN 'Held' THEN 'Pausada'
                WHEN 'Complete' THEN 'Finalizada'
                WHEN 'Stopped' THEN 'Finalizada'
                WHEN 'Aborted' THEN 'Alarma'
                WHEN 'Aborting' THEN 'Alarma'
                WHEN 'EN_PROCESO' THEN 'En proceso'
                WHEN 'SECUENCIA_INICIADA' THEN 'Secuencia iniciada'
                WHEN 'EN_ESPERA' THEN 'Esperando máquina'
                WHEN 'PAUSADA' THEN 'Pausada'
                WHEN 'FINALIZADA' THEN 'Finalizada'
                WHEN 'ERROR' THEN 'Alarma'
                ELSE 'Esperando máquina'
            END
        END AS value,
        planned_date,
        slot_idx,
        2 AS sort_time_order
    FROM SequenceStates
    
    UNION ALL
    
    -- Sequence planned end to terminate the block (capped at shift boundaries and current progress)
    SELECT 
        CASE 
            WHEN (CASE WHEN planned_end > @CurrentProgressTime THEN (CASE WHEN planned_start > @CurrentProgressTime THEN planned_start ELSE @CurrentProgressTime END) ELSE planned_end END) < @ShiftStartDT THEN @ShiftStartDT 
            WHEN (CASE WHEN planned_end > @CurrentProgressTime THEN (CASE WHEN planned_start > @CurrentProgressTime THEN planned_start ELSE @CurrentProgressTime END) ELSE planned_end END) > @ShiftEndDT THEN @ShiftEndDT
            ELSE (CASE WHEN planned_end > @CurrentProgressTime THEN (CASE WHEN planned_start > @CurrentProgressTime THEN planned_start ELSE @CurrentProgressTime END) ELSE planned_end END)
        END AS time,
        CONCAT(secuencia, CHAR(10), bastidor) AS metric,
        NULL AS value,
        planned_date,
        slot_idx,
        3 AS sort_time_order
    FROM SequenceStates
    
    UNION ALL
    
    -- Shift end boundary to force horizontal axis range
    SELECT 
        @ShiftEndDT AS time,
        CONCAT(secuencia, CHAR(10), bastidor) AS metric,
        NULL AS value,
        planned_date,
        slot_idx,
        4 AS sort_time_order
    FROM SequenceStates
) t
ORDER BY 
    COALESCE(planned_date, '1900-01-01') ASC, 
    slot_idx ASC, 
    metric ASC, 
    sort_time_order ASC;
"""

print("--- RUNNING PROPOSED TIMELINE QUERY ---")
try:
    cursor.execute(test_sql)
    rows = cursor.fetchall()
    print(f"Success! Returned {len(rows)} data rows.")
    for r in rows[:15]:
        print(f"time: {r[0]}, metric: {repr(r[1])}, value: {r[2]}")
except Exception as e:
    print(f"Error running query: {e}")

conn.close()
