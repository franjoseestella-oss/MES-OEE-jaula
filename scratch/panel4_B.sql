DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 CONVERT(varchar(8), FECHA_MONTAJE, 112) FROM LOG_TABLA WHERE TRY_CAST(FECHA_HORA_INICIO_SEC AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @DashboardDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @DashboardDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @DashboardDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

DECLARE @N INT = CEILING(@UnidadesAFabricar);

DECLARE @Count185 INT = 0;
SELECT @Count185 = COUNT(*)
FROM dbo.CALENDARIO_LABORAL
WHERE Laborable = 1 
  AND Cant_A_Fabricar = 18.5 
  AND Fecha <= @DashboardDate;

DECLARE @UseSecondSet185 BIT = 0;
IF @Count185 > 0 AND @Count185 % 2 = 0
    SET @UseSecondSet185 = 1;

DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < @ShiftStart
  AND log.OK_NOK = 'OK'
ORDER BY erp.id DESC;

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP
    WHERE fecha_montaje = @ActiveDate;
END

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP;
END;

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
        @ShiftStart AS time,
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
