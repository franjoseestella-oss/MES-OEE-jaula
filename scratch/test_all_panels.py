import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Test with a date in June, e.g. 2026-06-15
test_date = '2026-06-15'

common_prefix = """
SET NOCOUNT ON;
DECLARE @ActiveDate DATE = ?;

-- 1. Determine unidades a fabricar for the day
DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @ActiveDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

-- 2. Determine number of sequences to plan today
DECLARE @N INT = CEILING(@UnidadesAFabricar);

-- 3. Check odd/even of 18.5 days to select appropriate set from HHSS_18_5
DECLARE @Count185 INT = 0;
SELECT @Count185 = COUNT(*)
FROM dbo.CALENDARIO_LABORAL
WHERE Laborable = 1 
  AND Cant_A_Fabricar = 18.5 
  AND Fecha <= @ActiveDate;

DECLARE @UseSecondSet185 BIT = 0;
IF @Count185 > 0 AND @Count185 % 2 = 0
    SET @UseSecondSet185 = 1;

-- 4. Find the last completed sequence of the previous day
DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME))
  AND log.OK_NOK = 'OK'
ORDER BY erp.id DESC;

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP
    WHERE fecha_montaje = CONVERT(varchar(8), @ActiveDate, 112);
END

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP;
END

-- 5. Create temporary table for shift schedule times
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
"""

queries = {
    "Panel 1: SECUENCIAS PLANIFICADAS (TEÓRICO)": common_prefix + """
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@ActiveDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @ActiveDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @ActiveDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
)
SELECT COALESCE(MAX(seq_idx), 0) AS [Teórico]
FROM Planned_With_Times
WHERE [Fin Planificado] <= @EvalTime;
""",

    "Panel 2: SECUENCIAS COMPLETADAS (REAL)": common_prefix + """
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@ActiveDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @ActiveDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @ActiveDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
)
SELECT COUNT(*) AS [Real]
FROM Today_Seqs t
INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
  AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
  AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
  AND l.OK_NOK = 'OK';
""",

    "Panel 3: DESVIACIÓN (REAL - TEÓRICO)": common_prefix + """
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@ActiveDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @ActiveDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @ActiveDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
),
Teorico_Count AS (
    SELECT COALESCE(MAX(seq_idx), 0) AS teorico
    FROM Planned_With_Times
    WHERE [Fin Planificado] <= @EvalTime
),
Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
),
Real_Count AS (
    SELECT COUNT(*) AS real
    FROM Today_Seqs t
    INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
    WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
      AND l.OK_NOK = 'OK'
)
SELECT 
    r.real - t.teorico AS [Desviación]
FROM Real_Count r, Teorico_Count t;
""",

    "Panel 4 Target A: EVOLUCIÓN (TEÓRICO)": common_prefix + """
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME));

WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
)
SELECT time, [Teórico] FROM (
    SELECT 
        DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME)) AS time,
        0 AS [Teórico]
    UNION ALL
    SELECT 
        [Fin Planificado] AS time,
        seq_idx AS [Teórico]
    FROM Planned_With_Times
    WHERE [Fin Planificado] <= DATEADD(hour, 15, CAST(@ActiveDate AS DATETIME))
) t
ORDER BY time;
""",

    "Panel 4 Target B: EVOLUCIÓN (REAL)": common_prefix + """
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@ActiveDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @ActiveDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @ActiveDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
)
SELECT time, [Real] FROM (
    SELECT 
        DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME)) AS time,
        0 AS [Real]
    UNION ALL
    SELECT 
        TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AS time,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS [Real]
    FROM Today_Seqs t
    INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
    WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
      AND l.OK_NOK = 'OK'
) t
ORDER BY time;
"""
}

for name, q in queries.items():
    print(f"\n==========================================")
    print(f"Testing {name}...")
    print(f"==========================================")
    cursor.execute(q, test_date)
    rows = cursor.fetchall()
    print(f"Result count: {len(rows)}")
    for r in rows[:5]:
        print(r)
    if len(rows) > 5:
        print("...")

cursor.close()
conn.close()
