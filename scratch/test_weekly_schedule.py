import pyodbc

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

query = """
SET NOCOUNT ON;

-- Simulate active date
DECLARE @ActiveDate VARCHAR(8) = '20260608'; -- Using June 8, 2026, which has some runs

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @Monday DATE = DATEADD(wk, DATEDIFF(wk, 0, @SelectedDate), 0);
DECLARE @Friday DATE = DATEADD(day, 4, @Monday);

-- Create weekly schedule slots table
IF OBJECT_ID('tempdb..#WeeklyScheduleSlots') IS NOT NULL DROP TABLE #WeeklyScheduleSlots;
CREATE TABLE #WeeklyScheduleSlots (
    fecha DATE,
    slot_idx INT,
    horario TIME,
    PRIMARY KEY (fecha, slot_idx)
);

DECLARE @LoopDate DATE = @Monday;
WHILE @LoopDate <= @Friday
BEGIN
    DECLARE @DayCap DECIMAL(4,1);
    SELECT @DayCap = COALESCE(Cant_A_Fabricar, 18.0)
    FROM dbo.CALENDARIO_LABORAL
    WHERE Fecha = @LoopDate;

    IF @DayCap IS NULL SET @DayCap = 18.0;

    IF @DayCap = 18.0
    BEGIN
        INSERT INTO #WeeklyScheduleSlots (fecha, slot_idx, horario)
        SELECT @LoopDate, ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18;
    END
    ELSE IF @DayCap = 19.0
    BEGIN
        INSERT INTO #WeeklyScheduleSlots (fecha, slot_idx, horario)
        SELECT @LoopDate, ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_19;
    END
    ELSE IF @DayCap = 18.5
    BEGIN
        DECLARE @Cnt185 INT = 0;
        SELECT @Cnt185 = COUNT(*)
        FROM dbo.CALENDARIO_LABORAL
        WHERE Laborable = 1 
          AND Cant_A_Fabricar = 18.5 
          AND Fecha <= @LoopDate;

        IF @Cnt185 > 0 AND @Cnt185 % 2 = 0
        BEGIN
            INSERT INTO #WeeklyScheduleSlots (fecha, slot_idx, horario)
            SELECT @LoopDate, ROW_NUMBER() OVER (ORDER BY id), horario
            FROM dbo.HHSS_18_5
            WHERE id BETWEEN 20 AND 38;
        END
        ELSE
        BEGIN
            INSERT INTO #WeeklyScheduleSlots (fecha, slot_idx, horario)
            SELECT @LoopDate, ROW_NUMBER() OVER (ORDER BY id), horario
            FROM dbo.HHSS_18_5
            WHERE id BETWEEN 1 AND 19;
        END
    END
    ELSE
    BEGIN
        INSERT INTO #WeeklyScheduleSlots (fecha, slot_idx, horario)
        SELECT @LoopDate, ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18;
    END;

    SET @LoopDate = DATEADD(day, 1, @LoopDate);
END;

-- Get all runs within this week
IF OBJECT_ID('tempdb..#RunsThisWeek') IS NOT NULL DROP TABLE #RunsThisWeek;
SELECT 
    id,
    NBASTIDOR,
    FECHA_MONTAJE,
    OK_NOK,
    FECHA_HORA_INICIO_SEC,
    FECHA_HORA_FIN_SEC,
    TRY_CAST(CAST(COALESCE(FECHA_HORA_FIN_SEC, FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) AS run_date
INTO #RunsThisWeek
FROM dbo.LOG_TABLA
WHERE TRY_CAST(CAST(COALESCE(FECHA_HORA_FIN_SEC, FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) BETWEEN @Monday AND @Friday;

-- Candidates
IF OBJECT_ID('tempdb..#Candidates') IS NOT NULL DROP TABLE #Candidates;
SELECT 
    erp.id,
    erp.secuencia,
    erp.bastidor,
    erp.modelo,
    TRY_CAST(erp.fecha_montaje AS DATE) AS original_date,
    CAST(0 AS BIT) AS is_completed
INTO #Candidates
FROM dbo.JAULA_ERP erp
WHERE TRY_CAST(erp.fecha_montaje AS DATE) <= @Friday
  AND NOT EXISTS (
      SELECT 1 
      FROM dbo.LOG_TABLA l
      WHERE l.NBASTIDOR = erp.bastidor
        AND l.FECHA_MONTAJE = TRY_CAST(erp.fecha_montaje AS DATE)
        AND l.OK_NOK = 'OK'
        AND TRY_CAST(CAST(COALESCE(l.FECHA_HORA_FIN_SEC, l.FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) < @Monday
  );

-- Output rows
IF OBJECT_ID('tempdb..#OutputRows') IS NOT NULL DROP TABLE #OutputRows;
CREATE TABLE #OutputRows (
    id INT,
    secuencia VARCHAR(50),
    bastidor VARCHAR(50),
    modelo VARCHAR(50),
    original_date DATE,
    scheduled_date DATE,
    slot_idx INT,
    planned_start DATETIME,
    planned_end DATETIME,
    actual_start DATETIME,
    actual_end DATETIME,
    status VARCHAR(50),
    completed BIT,
    run_id FLOAT
);

DECLARE @D DATE = @Monday;
WHILE @D <= @Friday
BEGIN
    -- 1. Insert runs on day @D
    INSERT INTO #OutputRows (id, secuencia, bastidor, modelo, original_date, scheduled_date, slot_idx, actual_start, actual_end, status, completed, run_id)
    SELECT 
        c.id,
        c.secuencia,
        c.bastidor,
        c.modelo,
        c.original_date,
        @D,
        NULL,
        r.FECHA_HORA_INICIO_SEC,
        r.FECHA_HORA_FIN_SEC,
        r.OK_NOK,
        CASE WHEN r.OK_NOK = 'OK' THEN 1 ELSE 0 END,
        r.id
    FROM #Candidates c
    INNER JOIN #RunsThisWeek r ON r.NBASTIDOR = c.bastidor AND r.FECHA_MONTAJE = c.original_date
    WHERE r.run_date = @D;

    -- Mark candidates that succeeded on @D as completed
    UPDATE c
    SET c.is_completed = 1
    FROM #Candidates c
    INNER JOIN #RunsThisWeek r ON r.NBASTIDOR = c.bastidor AND r.FECHA_MONTAJE = c.original_date
    WHERE r.run_date = @D AND r.OK_NOK = 'OK';

    -- 2. Schedule pending sequences
    DECLARE @Cap INT;
    SELECT @Cap = COUNT(*) FROM #WeeklyScheduleSlots WHERE fecha = @D;

    DECLARE @RunsCount INT;
    SELECT @RunsCount = COUNT(*) FROM #OutputRows WHERE scheduled_date = @D;

    DECLARE @Available INT = @Cap - @RunsCount;

    IF @Available > 0
    BEGIN
        IF OBJECT_ID('tempdb..#ToSchedule') IS NOT NULL DROP TABLE #ToSchedule;
        
        SELECT TOP (@Available) c.id
        INTO #ToSchedule
        FROM #Candidates c
        WHERE c.is_completed = 0
          AND c.original_date <= @D
          AND NOT EXISTS (
              SELECT 1 FROM #OutputRows o 
              WHERE o.scheduled_date = @D AND o.id = c.id
          )
        ORDER BY c.id ASC;

        INSERT INTO #OutputRows (id, secuencia, bastidor, modelo, original_date, scheduled_date, slot_idx, actual_start, actual_end, status, completed, run_id)
        SELECT 
            c.id,
            c.secuencia,
            c.bastidor,
            c.modelo,
            c.original_date,
            @D,
            NULL,
            NULL,
            NULL,
            'Pendiente',
            0,
            NULL
        FROM #Candidates c
        INNER JOIN #ToSchedule ts ON ts.id = c.id;
    END;

    SET @D = DATEADD(day, 1, @D);
END;

-- Assign slot_idx using CTE
WITH Ordered AS (
    SELECT 
        slot_idx,
        ROW_NUMBER() OVER (PARTITION BY scheduled_date ORDER BY completed DESC, id ASC) as new_slot
    FROM #OutputRows
)
UPDATE Ordered
SET slot_idx = new_slot;

-- Assign planned_start and planned_end
UPDATE o
SET 
    o.planned_start = DATEADD(second, 
        CASE 
            WHEN o.slot_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(o.scheduled_date AS DATETIME))
    ),
    o.planned_end = DATEADD(second, 
        DATEDIFF(second, '07:00:00', COALESCE(t_curr.horario, '07:00:00')),
        DATEADD(hour, 7, CAST(o.scheduled_date AS DATETIME))
    )
FROM #OutputRows o
LEFT JOIN #WeeklyScheduleSlots t_curr ON t_curr.fecha = o.scheduled_date AND t_curr.slot_idx = o.slot_idx
LEFT JOIN #WeeklyScheduleSlots t_prev ON t_prev.fecha = o.scheduled_date AND t_prev.slot_idx = o.slot_idx - 1;

-- Output results
SELECT 
    ROW_NUMBER() OVER (ORDER BY s.scheduled_date ASC, s.slot_idx ASC) AS [ID],
    s.secuencia AS [Secuencia],
    s.bastidor AS [Bastidor],
    s.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), s.scheduled_date, 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), s.planned_start, 108) AS [Inicio Planificado],
    CONVERT(varchar(8), s.planned_end, 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(s.actual_start AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(s.actual_end AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN s.actual_end IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, s.planned_end, CAST(CAST(s.actual_end AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, s.planned_end, CAST(CAST(s.actual_end AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, s.planned_end, CAST(CAST(s.actual_end AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    s.status AS [Estado]
FROM #OutputRows s
ORDER BY s.scheduled_date ASC, s.slot_idx ASC;
"""

cursor.execute(query)
rows = cursor.fetchall()
print("ID | Secuencia | Bastidor | Modelo | Fecha Montaje | Inicio Plan | Fin Plan | Estado")
for r in rows[:40]:
    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[10]}")
