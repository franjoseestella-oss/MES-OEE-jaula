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
DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = TRY_CAST(@ActiveDate AS DATE);

DECLARE @ShiftStartHour INT = 7, @ShiftEndHour INT = 15;
DECLARE @ShiftStartStr VARCHAR(8) = '07:00:00';

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStartDT DATETIME = DATEADD(hour, @ShiftStartHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @ShiftEndDT DATETIME = DATEADD(hour, @ShiftEndHour - @UTCOffset, CAST(@PlotDate AS DATETIME));

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

UPDATE s
SET 
    s.planned_start = DATEADD(hour, -@UTCOffset, DATEADD(second, 
        CASE 
            WHEN m.slot_idx = 1 THEN 0
            ELSE DATEDIFF(second, @ShiftStartStr, COALESCE(t_prev.horario, @ShiftStartStr))
        END,
        DATEADD(hour, @ShiftStartHour, CAST(@PlotDate AS DATETIME))
    )),
    s.planned_end = DATEADD(hour, -@UTCOffset, CASE 
        WHEN m.horario IS NOT NULL THEN 
            DATEADD(second, 
                DATEDIFF(second, @ShiftStartStr, m.horario), 
                DATEADD(hour, @ShiftStartHour, CAST(@PlotDate AS DATETIME)) 
            )
        ELSE
            DATEADD(minute, 25, 
                DATEADD(second, 
                    CASE 
                        WHEN m.slot_idx = 1 THEN 0 
                        ELSE DATEDIFF(second, @ShiftStartStr, COALESCE(t_prev.horario, @ShiftStartStr)) 
                    END, 
                    DATEADD(hour, @ShiftStartHour, CAST(@PlotDate AS DATETIME)) 
                ) 
            )
    END)
FROM #SeqsToSchedule s
INNER JOIN #MappedSeqs m ON m.id = s.id
LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = m.planned_date AND t_prev.slot_idx_in_day = m.slot_idx - 1;

-- Find active slot index in progress
DECLARE @ActiveSlotIdx INT;
SELECT @ActiveSlotIdx = MIN(slot_idx)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;

-- Find theoretical active slot index
DECLARE @TheoreticalActiveSlotIdx INT;
SELECT TOP 1 @TheoreticalActiveSlotIdx = slot_idx
FROM #SeqsToSchedule
WHERE planned_start <= @CurrentProgressTime AND planned_end >= @CurrentProgressTime;

IF @TheoreticalActiveSlotIdx IS NULL
BEGIN
    SELECT @TheoreticalActiveSlotIdx = COALESCE(
        (SELECT MAX(slot_idx) FROM #SeqsToSchedule WHERE planned_start <= @CurrentProgressTime),
        1
    );
END;

SELECT 
    @PlotDate AS plot_date,
    @ShiftStartDT AS shift_start,
    @ShiftEndDT AS shift_end,
    @CurrentProgressTime AS cur_progress,
    @UTCOffset AS utc_offset;

-- Query the alarm intervals
SELECT 'ALARM_INTERVALS' AS marker;
WITH AlarmIntervals AS (
    SELECT 
        FECHA_Y_HORA,
        DURACION,
        DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END)) AS alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN @CurrentProgressTime
            ELSE DATEADD(second, COALESCE(parts.hrs * 3600 + parts.mins * 60 + parts.secs, 0), 
                 DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END)))
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
)
SELECT * FROM AlarmIntervals;

SELECT 'SEQS_TO_SCHEDULE' AS marker;
SELECT id, secuencia, bastidor, planned_start, planned_end, actual_start, actual_end FROM #SeqsToSchedule;
"""

cursor.execute(query)
while True:
    try:
        if cursor.description is not None:
            print("--- RESULTS ---")
            for r in cursor.fetchall():
                print(r)
    except Exception as e:
        print("Error fetching:", e)
    if not cursor.nextset():
        break
conn.close()
