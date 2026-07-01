import json

sql_query_panel_10 = """DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());

-- Active reference/sequence currently in cycles (from HMI/PLC)
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
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) AS actual_completion_date,
        CAST(CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_start,
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_end,
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
    actual_end DATETIME,
    shift_start DATETIME,
    shift_end DATETIME,
    progress_time DATETIME
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
WHERE $__timeFilter(m.planned_date);

-- Calculate shift start/end, progress time, and planned start/end for each sequence
UPDATE s
SET 
    s.shift_start = DATEADD(hour, 7 - @UTCOffset, CAST(s.planned_date AS DATETIME)),
    s.shift_end = DATEADD(hour, 15 - @UTCOffset, CAST(s.planned_date AS DATETIME)),
    s.progress_time = CASE 
        WHEN CAST(GETDATE() AS DATE) = s.planned_date THEN GETUTCDATE()
        WHEN s.planned_date > CAST(GETDATE() AS DATE) THEN DATEADD(hour, 7 - @UTCOffset, CAST(s.planned_date AS DATETIME))
        ELSE DATEADD(hour, 15 - @UTCOffset, CAST(s.planned_date AS DATETIME))
    END,
    s.planned_start = DATEADD(hour, -@UTCOffset, DATEADD(second, 
        CASE 
            WHEN m.slot_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
    )),
    s.planned_end = DATEADD(hour, -@UTCOffset, CASE 
        WHEN m.horario IS NOT NULL THEN 
            DATEADD(second, 
                DATEDIFF(second, '07:00:00', m.horario),
                DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
            )
        ELSE
            DATEADD(minute, 25, 
                DATEADD(second, 
                    CASE 
                        WHEN m.slot_idx = 1 THEN 0
                        ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                    END,
                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                )
            )
    END)
FROM #SeqsToSchedule s
INNER JOIN #MappedSeqs m ON m.id = s.id
LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = m.planned_date AND t_prev.slot_idx_in_day = m.slot_idx - 1;

-- Find active slot ID in progress globally
DECLARE @ActiveSeqId INT;
SELECT @ActiveSeqId = MIN(id)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;

-- Find theoretical active sequence ID
DECLARE @TheoreticalActiveSeqId INT;
SELECT TOP 1 @TheoreticalActiveSeqId = id
FROM #SeqsToSchedule
WHERE planned_start <= progress_time AND planned_end >= progress_time;

IF @TheoreticalActiveSeqId IS NULL
BEGIN
    SELECT @TheoreticalActiveSeqId = COALESCE(
        (SELECT MAX(id) FROM #SeqsToSchedule WHERE planned_start <= progress_time),
        (SELECT MIN(id) FROM #SeqsToSchedule),
        1
    );
END;

-- Alarm intervals CTE: we support multiple days by converting alarms to their actual dates
WITH AlarmIntervals AS (
    SELECT 
        DATEADD(hour, -@UTCOffset, 
            CASE 
                WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103)
                ELSE TRY_CAST(CONVERT(VARCHAR(10), GETDATE(), 120) + ' ' + FECHA_Y_HORA AS DATETIME)
            END
        ) AS alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN 
                CASE 
                    WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN GETUTCDATE()
                    ELSE DATEADD(hour, -@UTCOffset, GETDATE())
                END
            ELSE DATEADD(second, COALESCE(parts.hrs * 3600 + parts.mins * 60 + parts.secs, 0), 
                 DATEADD(hour, -@UTCOffset, 
                     CASE 
                         WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103)
                         ELSE TRY_CAST(CONVERT(VARCHAR(10), GETDATE(), 120) + ' ' + FECHA_Y_HORA AS DATETIME)
                     END
                 ))
        END AS alarm_end
    FROM dbo.LOG_ALARMAS
    CROSS APPLY (
        SELECT REPLACE(DURACION, ' ', '') AS clean_dur
    ) cd
    CROSS APPLY (
        SELECT 
            CHARINDEX('h', cd.clean_dur) AS h_pos,
            CHARINDEX('m', cd.clean_dur) AS m_pos,
            CHARINDEX('s', cd.clean_dur) AS s_pos
    ) pos
    CROSS APPLY (
        SELECT 
            CASE WHEN pos.h_pos > 0 THEN TRY_CAST(SUBSTRING(cd.clean_dur, 1, pos.h_pos - 1) AS INT) ELSE 0 END AS hrs,
            CASE 
                WHEN pos.m_pos > 0 THEN 
                    TRY_CAST(SUBSTRING(cd.clean_dur, 
                        CASE WHEN pos.h_pos > 0 THEN pos.h_pos + 1 ELSE 1 END, 
                        pos.m_pos - CASE WHEN pos.h_pos > 0 THEN pos.h_pos + 1 ELSE 1 END
                    ) AS INT)
                ELSE 0 
            END AS mins,
            CASE 
                WHEN pos.s_pos > 0 THEN 
                    TRY_CAST(SUBSTRING(cd.clean_dur, 
                        CASE 
                            WHEN pos.m_pos > 0 THEN pos.m_pos + 1 
                            WHEN pos.h_pos > 0 THEN pos.h_pos + 1 
                            ELSE 1 
                        END, 
                        pos.s_pos - CASE 
                            WHEN pos.m_pos > 0 THEN pos.m_pos + 1 
                            WHEN pos.h_pos > 0 THEN pos.h_pos + 1 
                            ELSE 1 
                        END
                    ) AS INT)
                ELSE 0 
            END AS secs
    ) parts
    WHERE FECHA_Y_HORA LIKE '[0-9]%' OR FECHA_Y_HORA LIKE '[0-9][0-9]%'
),
RawTimestamps AS (
    SELECT id, planned_start AS t FROM #SeqsToSchedule
    UNION
    SELECT id, planned_end AS t FROM #SeqsToSchedule
    UNION
    SELECT id, actual_start AS t FROM #SeqsToSchedule WHERE actual_start IS NOT NULL
    UNION
    SELECT id, actual_end AS t FROM #SeqsToSchedule WHERE actual_end IS NOT NULL
    UNION
    SELECT id, progress_time AS t FROM #SeqsToSchedule
    UNION
    SELECT s.id, a.alarm_start AS t 
    FROM #SeqsToSchedule s
    CROSS JOIN AlarmIntervals a
    WHERE a.alarm_start BETWEEN s.planned_start AND s.shift_end
    UNION
    SELECT s.id, a.alarm_end AS t 
    FROM #SeqsToSchedule s
    CROSS JOIN AlarmIntervals a
    WHERE a.alarm_end BETWEEN s.planned_start AND s.shift_end
),
BoundedTimestamps AS (
    SELECT DISTINCT
        bt.id,
        CASE 
            WHEN bt.t < s.shift_start THEN s.shift_start
            WHEN bt.t > s.shift_end THEN s.shift_end
            ELSE bt.t
        END AS t
    FROM RawTimestamps bt
    INNER JOIN #SeqsToSchedule s ON s.id = bt.id
),
FilteredTimestamps AS (
    SELECT bt.id, bt.t
    FROM BoundedTimestamps bt
    INNER JOIN #SeqsToSchedule s ON s.id = bt.id
    WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start ELSE s.planned_start 
                  END
      AND bt.t <= CASE 
                      -- Rule: If a previous sequence is in progress, do not draw this sequence
                      WHEN @ActiveSeqId IS NOT NULL AND s.id > @ActiveSeqId AND s.actual_start IS NULL AND @ActiveSeqId >= @TheoreticalActiveSeqId THEN
                          s.planned_start
                      
                      WHEN s.actual_start IS NOT NULL THEN
                          CASE 
                               WHEN s.actual_end IS NOT NULL THEN 
                                   CASE WHEN s.actual_end > s.planned_end THEN s.actual_end ELSE s.planned_end END
                               ELSE s.progress_time
                          END
                      ELSE
                          CASE 
                              WHEN s.planned_start >= s.progress_time THEN s.planned_start
                              ELSE
                                  CASE 
                                      WHEN s.planned_end > s.progress_time THEN s.progress_time
                                      ELSE s.planned_end
                                  END
                          END
                  END
)
SELECT time, metric, value FROM (
    -- Shift start boundary
    SELECT 
        s.shift_start AS time,
        CONCAT(s.secuencia, CHAR(10), s.bastidor) AS metric,
        NULL AS value,
        s.planned_date,
        s.slot_idx,
        1 AS sort_time_order
    FROM #SeqsToSchedule s
    
    UNION ALL
    
    -- Shift end boundary
    SELECT 
        s.shift_end AS time,
        CONCAT(s.secuencia, CHAR(10), s.bastidor) AS metric,
        NULL AS value,
        s.planned_date,
        s.slot_idx,
        4 AS sort_time_order
    FROM #SeqsToSchedule s
    
    UNION ALL
    
    -- Active states
    SELECT 
        ft.t AS time,
        CONCAT(s.secuencia, CHAR(10), s.bastidor) AS metric,
        CASE 
            WHEN ft.t >= CASE 
                            -- Rule: If a previous sequence is in progress, do not draw this sequence
                            WHEN @ActiveSeqId IS NOT NULL AND s.id > @ActiveSeqId AND s.actual_start IS NULL AND @ActiveSeqId >= @TheoreticalActiveSeqId THEN
                                s.planned_start
                            
                            WHEN s.actual_start IS NOT NULL THEN
                                CASE 
                                    WHEN s.actual_end IS NOT NULL THEN 
                                        CASE WHEN s.actual_end > s.planned_end THEN s.actual_end ELSE s.planned_end END
                                    ELSE s.progress_time
                                END
                            ELSE
                                CASE 
                                    WHEN s.planned_start >= s.progress_time THEN s.planned_start
                                    ELSE
                                        CASE 
                                            WHEN s.planned_end > s.progress_time THEN s.progress_time
                                            ELSE s.planned_end
                                        END
                                END
                        END THEN NULL
            WHEN s.actual_start IS NOT NULL AND s.actual_start >= s.planned_end AND ft.t >= s.planned_end AND ft.t < s.actual_start THEN NULL
            WHEN s.id = COALESCE(
                     (SELECT MIN(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND actual_start IS NOT NULL AND actual_start <= ft.t AND (actual_end IS NULL OR actual_end > ft.t)),
                     (SELECT TOP 1 id FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND planned_start <= ft.t AND planned_end >= ft.t),
                     (SELECT MAX(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND planned_start <= ft.t),
                     (SELECT MIN(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date),
                     s.id
                 )
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'
            WHEN s.id = COALESCE(
                     (SELECT MIN(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND actual_start IS NOT NULL AND actual_start <= ft.t AND (actual_end IS NULL OR actual_end > ft.t)),
                     (SELECT TOP 1 id FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND planned_start <= ft.t AND planned_end >= ft.t),
                     (SELECT MAX(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date AND planned_start <= ft.t),
                     (SELECT MIN(id) FROM #SeqsToSchedule WHERE planned_date = s.planned_date),
                     s.id
                 )
                 AND (s.actual_start IS NULL OR ft.t < s.actual_start)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'
            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN
                CASE 
                    WHEN ft.t < s.planned_start OR ft.t >= s.planned_end THEN 'Exceso de tiempo'
                    ELSE 'En proceso'
                END
            ELSE 'Esperando máquina'
        END AS value,
        s.planned_date,
        s.slot_idx,
        2 AS sort_time_order
    FROM FilteredTimestamps ft
    INNER JOIN #SeqsToSchedule s ON s.id = ft.id
) t
ORDER BY 
    COALESCE(planned_date, '1900-01-01') ASC, 
    slot_idx ASC, 
    metric ASC, 
    time ASC,
    sort_time_order ASC;"""

sql_query_panel_5 = """DECLARE @SelectedDateStart DATE = CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);
DECLARE @SelectedDateEnd DATE = CAST(CAST($__timeTo() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);

DECLARE @ShiftStartStr VARCHAR(8);
DECLARE @ShiftStartHour INT;

SELECT 
    @ShiftStartStr = CAST(hora_inicio_jornada AS VARCHAR(8)),
    @ShiftStartHour = DATEPART(hour, hora_inicio_jornada)
FROM dbo.TURNO_TRABAJO;

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
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) AS actual_completion_date,
        CAST(CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_start,
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_end,
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

-- Get completion status from log
IF OBJECT_ID('tempdb..#SeqsWithLog') IS NOT NULL DROP TABLE #SeqsWithLog;
SELECT 
    m.id,
    m.secuencia,
    m.bastidor,
    m.modelo,
    m.original_date,
    m.planned_date,
    m.slot_idx,
    m.horario,
    l.OK_NOK AS log_status,
    l.FECHA_MONTAJE AS log_fecha_montaje,
    CAST(CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS FECHA_HORA_INICIO_SEC,
    CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS FECHA_HORA_FIN_SEC
INTO #SeqsWithLog
FROM #MappedSeqs m
LEFT JOIN (
    SELECT 
        id,
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) l ON l.NBASTIDOR = m.bastidor AND l.rn = 1;

SELECT 
    ROW_NUMBER() OVER (ORDER BY s.slot_idx ASC, s.secuencia ASC) AS [ID],
    s.secuencia AS [Secuencia],
    s.bastidor AS [Bastidor],
    s.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), s.planned_date, 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), 
        DATEADD(second, 
            CASE 
                WHEN s.slot_idx = 1 THEN 0
                ELSE DATEDIFF(second, @ShiftStartStr, COALESCE(t_prev.horario, @ShiftStartStr))
            END,
            DATEADD(hour, @ShiftStartHour, CAST(s.planned_date AS DATETIME))
        ), 
        108
    ) AS [Inicio Planificado],
    CONVERT(varchar(8), 
        DATEADD(second, 
            DATEDIFF(second, @ShiftStartStr, COALESCE(s.horario, @ShiftStartStr)),
            DATEADD(hour, @ShiftStartHour, CAST(s.planned_date AS DATETIME))
        ), 
        108
    ) AS [Fin Planificado],
    CONVERT(varchar(8), s.FECHA_HORA_INICIO_SEC, 108) AS [Inicio Real],
    CONVERT(varchar(8), s.FECHA_HORA_FIN_SEC, 108) AS [Fin Real],
    CASE 
        WHEN s.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, 
                    DATEADD(second, 
                        DATEDIFF(second, @ShiftStartStr, COALESCE(s.horario, @ShiftStartStr)),
                        DATEADD(hour, @ShiftStartHour, CAST(s.planned_date AS DATETIME))
                    ), 
                    s.FECHA_HORA_FIN_SEC
                ) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, 
                        DATEADD(second, 
                            DATEDIFF(second, @ShiftStartStr, COALESCE(s.horario, @ShiftStartStr)),
                            DATEADD(hour, @ShiftStartHour, CAST(s.planned_date AS DATETIME))
                        ), 
                        s.FECHA_HORA_FIN_SEC
                    ) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, 
                        DATEADD(second, 
                            DATEDIFF(second, @ShiftStartStr, COALESCE(s.horario, @ShiftStartStr)),
                            DATEADD(hour, @ShiftStartHour, CAST(s.planned_date AS DATETIME))
                        ), 
                        s.FECHA_HORA_FIN_SEC
                    ) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    CASE 
        WHEN s.FECHA_HORA_FIN_SEC IS NOT NULL THEN s.log_status
        WHEN active.id IS NOT NULL OR (s.FECHA_HORA_INICIO_SEC IS NOT NULL AND s.FECHA_HORA_FIN_SEC IS NULL) THEN 'Procesando'
        ELSE 'Pendiente'
    END AS [Estado]
FROM #SeqsWithLog s
LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = s.planned_date AND t_prev.slot_idx_in_day = s.slot_idx - 1
LEFT JOIN dbo.REFERENCIA_EN_CICLO active ON active.NBASTIDOR = s.bastidor
WHERE 
    s.planned_date BETWEEN @SelectedDateStart AND @SelectedDateEnd
ORDER BY s.slot_idx ASC, s.secuencia ASC;"""

sql_query_panel_1 = """DECLARE @SelectedDateStart DATE = CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);
DECLARE @SelectedDateEnd DATE = CAST(CAST($__timeTo() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);

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
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) AS actual_completion_date,
        CAST(CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_start,
        CAST(CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS actual_end,
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

DECLARE @Teorico INT, @Real INT, @OK INT, @NOK INT;

SELECT @Teorico = COUNT(*)
FROM #MappedSeqs
WHERE planned_date BETWEEN @SelectedDateStart AND @SelectedDateEnd;

SELECT 
    @Real = COUNT(DISTINCT log.NBASTIDOR),
    @OK = COUNT(DISTINCT CASE WHEN log.OK_NOK = 'OK' THEN log.NBASTIDOR END),
    @NOK = COUNT(DISTINCT CASE WHEN log.OK_NOK = 'NOK' THEN log.NBASTIDOR END)
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) BETWEEN @SelectedDateStart AND @SelectedDateEnd;

SELECT 
    COALESCE(@Teorico, 0) AS [PLANIFICADAS (TEÓRICO)],
    COALESCE(@Real, 0) AS [COMPLETADAS (REAL)],
    COALESCE(@OK, 0) AS [SECUENCIAS OK],
    COALESCE(@NOK, 0) AS [SECUENCIAS NOK],
    COALESCE(@Real, 0) - COALESCE(@Teorico, 0) AS [DESVIACIÓN];"""

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    data = json.load(f)

updated_p1 = False
updated_p5 = False
updated_p10 = False

for p in data.get("panels", []):
    pid = p.get("id")
    if pid == 1:
        p["targets"][0]["rawSql"] = sql_query_panel_1
        updated_p1 = True
    elif pid == 5:
        p["targets"][0]["rawSql"] = sql_query_panel_5
        updated_p5 = True
    elif pid == 10:
        p["targets"][0]["rawSql"] = sql_query_panel_10
        updated_p10 = True

if updated_p1 and updated_p5 and updated_p10:
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Success: Local dashboard JSON has been updated for Panels 1, 5, and 10.")
else:
    print(f"Error: Missing panels. P1: {updated_p1}, P5: {updated_p5}, P10: {updated_p10}")
