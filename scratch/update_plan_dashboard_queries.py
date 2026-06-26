import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

# Read the existing dashboard
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

# Define the new SQL queries for each panel and target
queries = {
    # Panel 1: SECUENCIAS PLANIFICADAS (TEÓRICO)
    (1, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
CREATE TABLE #CalendarSlots (
    global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE
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
INSERT INTO #CalendarSlots (fecha)
SELECT 
    cb.Fecha
FROM CalendarBase cb
CROSS APPLY (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18
    WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_19
    WHERE cb.Cant_A_Fabricar = 19.0
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 1 AND id BETWEEN 1 AND 19
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 0 AND id BETWEEN 20 AND 38
) s
WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
ORDER BY cb.Fecha ASC, s.seq_idx ASC;

IF OBJECT_ID('tempdb..#MappedSeqs') IS NOT NULL DROP TABLE #MappedSeqs;
CREATE TABLE #MappedSeqs (
    id INT PRIMARY KEY,
    planned_date DATE
);

WITH OrderedERP AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
INSERT INTO #MappedSeqs (id, planned_date)
SELECT 
    o.id,
    cs.fecha
FROM OrderedERP o
INNER JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

SELECT COUNT(*) AS [Teórico]
FROM #MappedSeqs
WHERE planned_date = @SelectedDate;""",

    # Panel 2: SECUENCIAS COMPLETADAS (REAL)
    (2, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

SELECT COUNT(DISTINCT log.NBASTIDOR) AS [Real]
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_MONTAJE = TRY_CAST(@ActiveDate AS DATE);""",

    # Panel 3: DESVIACIÓN (REAL - TEÓRICO)
    (3, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
CREATE TABLE #CalendarSlots (
    global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE
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
INSERT INTO #CalendarSlots (fecha)
SELECT 
    cb.Fecha
FROM CalendarBase cb
CROSS APPLY (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18
    WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_19
    WHERE cb.Cant_A_Fabricar = 19.0
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 1 AND id BETWEEN 1 AND 19
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 0 AND id BETWEEN 20 AND 38
) s
WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
ORDER BY cb.Fecha ASC, s.seq_idx ASC;

IF OBJECT_ID('tempdb..#MappedSeqs') IS NOT NULL DROP TABLE #MappedSeqs;
CREATE TABLE #MappedSeqs (
    id INT PRIMARY KEY,
    planned_date DATE
);

WITH OrderedERP AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
INSERT INTO #MappedSeqs (id, planned_date)
SELECT 
    o.id,
    cs.fecha
FROM OrderedERP o
INNER JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

DECLARE @Teorico INT, @Real INT;

SELECT @Teorico = COUNT(*)
FROM #MappedSeqs
WHERE planned_date = @SelectedDate;

SELECT @Real = COUNT(DISTINCT log.NBASTIDOR)
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_MONTAJE = TRY_CAST(@ActiveDate AS DATE);

SELECT COALESCE(@Real, 0) - COALESCE(@Teorico, 0) AS [Desviación];""",

    # Panel 4: EVOLUCIÓN PLAN DE PRODUCCIÓN (PLAN vs REAL)
    # Target A: Teórico
    (4, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = CAST($__timeFrom() AS DATE);

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));

DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @DashboardDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

DECLARE @Count185 INT = 0;
SELECT @Count185 = COUNT(*)
FROM dbo.CALENDARIO_LABORAL
WHERE Laborable = 1 
  AND Cant_A_Fabricar = 18.5 
  AND Fecha <= @DashboardDate;

DECLARE @UseSecondSet185 BIT = 0;
IF @Count185 > 0 AND @Count185 % 2 = 0
    SET @UseSecondSet185 = 1;

IF OBJECT_ID('tempdb..#ShiftSchedule') IS NOT NULL
    DROP TABLE #ShiftSchedule;

CREATE TABLE #ShiftSchedule (
    seq_idx INT,
    horario TIME
);

IF @UnidadesAFabricar = 18.0
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END
ELSE IF @UnidadesAFabricar = 19.0
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_19;
END
ELSE IF @UnidadesAFabricar = 18.5
BEGIN
    IF @UseSecondSet185 = 1
    BEGIN
        INSERT INTO #ShiftSchedule (seq_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 20 AND 38;
    END
    ELSE
    BEGIN
        INSERT INTO #ShiftSchedule (seq_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 1 AND 19;
    END
END
ELSE
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END;

WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        DATEADD(hour, -@UTCOffset, CAST(CONCAT(CONVERT(VARCHAR(10), @PlotDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME)) AS [Fin Planificado]
    FROM #ShiftSchedule s
)
SELECT time, [Teórico] FROM (
    SELECT 
        @ShiftStart AS time,
        0 AS [Teórico]
    UNION ALL
    SELECT 
        [Fin Planificado] AS time,
        seq_idx AS [Teórico]
    FROM Planned_With_Times
    WHERE [Fin Planificado] <= DATEADD(hour, 15 - @UTCOffset, CAST(@PlotDate AS DATETIME))
) t
ORDER BY time;""",

    # Target B: Real
    (4, "B"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = CAST($__timeFrom() AS DATE);

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));

SELECT time, [Real] FROM (
    SELECT 
        @ShiftStart AS time,
        0 AS [Real]
    UNION ALL
    SELECT 
        DATEADD(hour, -@UTCOffset, TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS time,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS [Real]
    FROM dbo.LOG_TABLA l
    WHERE CAST(l.FECHA_MONTAJE AS DATE) = @DashboardDate
      AND l.OK_NOK = 'OK'
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME))
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME))
) t
ORDER BY time;""",

    # Panel 5: LISTADO DE SECUENCIAS (PLAN vs REAL)
    (5, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @Monday DATE = DATEADD(wk, DATEDIFF(wk, 0, @SelectedDate), 0);
DECLARE @Friday DATE = DATEADD(day, 4, @Monday);

-- Create weekly schedule slots table
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
    l.FECHA_HORA_INICIO_SEC,
    l.FECHA_HORA_FIN_SEC
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

-- Now assign planned times ONLY if planned_date is within the current week
SELECT 
    ROW_NUMBER() OVER (ORDER BY COALESCE(s.planned_date, '1900-01-01') ASC, s.slot_idx ASC, s.secuencia ASC) AS [ID],
    s.secuencia AS [Secuencia],
    s.bastidor AS [Bastidor],
    s.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), s.planned_date, 103), '') AS [Fecha Montaje],
    -- Planned Times are ONLY shown if planned_date falls within the active week
    CASE 
        WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
            CONVERT(varchar(8), 
                DATEADD(second, 
                    CASE 
                        WHEN s.slot_idx = 1 THEN 0
                        ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                    END,
                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                ), 
                108
            )
        ELSE ''
    END AS [Inicio Planificado],
    CASE 
        WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
            CONVERT(varchar(8), 
                DATEADD(second, 
                    DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                ), 
                108
            )
        ELSE ''
    END AS [Fin Planificado],
    CONVERT(varchar(8), CAST(s.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN s.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            -- Deviation is only calculated if planned times exist
            CASE 
                WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
                    CASE 
                        WHEN DATEDIFF(minute, 
                            DATEADD(second, 
                                DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                            ), 
                            CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                        ) > 0 
                            THEN '+' + CAST(DATEDIFF(minute, 
                                DATEADD(second, 
                                    DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                                ), 
                                CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                            ) AS VARCHAR) + ' min'
                        ELSE 
                            CAST(DATEDIFF(minute, 
                                DATEADD(second, 
                                    DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                                ), 
                                CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                            ) AS VARCHAR) + ' min'
                    END
                ELSE '-'
            END
    END AS [Desviación],
    COALESCE(s.log_status, 'Pendiente') AS [Estado]
FROM #SeqsWithLog s
LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = s.planned_date AND t_prev.slot_idx_in_day = s.slot_idx - 1
WHERE 
    -- Show sequences planned for this week
    (s.planned_date BETWEEN @Monday AND @Friday)
    -- OR sequences planned for the past (or not planned / < 227) that are either NOT completed, or completed during this week
    OR (
        (s.planned_date < @Monday OR s.planned_date IS NULL)
        AND (
            s.log_status IS NULL 
            OR s.log_status = 'NOK' 
            -- Completed this week
            OR CAST(s.log_fecha_montaje AS DATE) BETWEEN @Monday AND @Friday
        )
    )
ORDER BY COALESCE(s.planned_date, '1900-01-01') ASC, s.slot_idx ASC, s.secuencia ASC;""",

    # Panel 10: Plan de Producción por Secuencias (Teórico vs Real)
    (10, "A"): """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = CAST($__timeFrom() AS DATE);

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
    planned_end DATETIME
);

INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, modelo, completed, status, completion_time)
SELECT 
    m.id,
    m.secuencia,
    m.bastidor,
    m.modelo,
    CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
    COALESCE(log.OK_NOK, 'Pendiente'),
    log.FECHA_HORA_FIN_SEC
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
WHERE m.planned_date = @SelectedDate;

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
        NULL AS value
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
        END AS value
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
        NULL AS value
    FROM SequenceStates
    
    UNION ALL
    
    -- Shift end boundary to force horizontal axis range
    SELECT 
        @ShiftEndDT AS time,
        CONCAT(secuencia, CHAR(10), bastidor) AS metric,
        NULL AS value
    FROM SequenceStates
) t
}

with open("scratch/panel10_query_full.sql", "r", encoding="utf-8") as f:
    queries[(10, "A")] = f.read()

# Update SQL in targets
updated_count = 0
for panel in db.get("panels", []):
    pid = panel.get("id")
    for target in panel.get("targets", []):
        ref_id = target.get("refId")
        key = (pid, ref_id)
        if key in queries:
            target["rawSql"] = queries[key]
            updated_count += 1
            print(f"Updated Panel ID {pid} Target {ref_id}")

# Save updated dashboard
with open(filepath, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Dashboard updated successfully. Total query targets modified: {updated_count}")
