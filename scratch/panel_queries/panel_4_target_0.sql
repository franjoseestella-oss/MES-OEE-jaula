DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE), 112);

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @PlotDate DATE = CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);

DECLARE @ShiftStartHour INT, @ShiftEndHour INT;
SELECT 
    @ShiftStartHour = DATEPART(hour, hora_inicio_jornada),
    @ShiftEndHour = DATEPART(hour, hora_fin_jornada)
FROM dbo.TURNO_TRABAJO;

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStart DATETIME = DATEADD(hour, @ShiftStartHour - @UTCOffset, CAST(@PlotDate AS DATETIME));

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
    WHERE [Fin Planificado] <= DATEADD(hour, @ShiftEndHour - @UTCOffset, CAST(@PlotDate AS DATETIME))
) t
ORDER BY time;