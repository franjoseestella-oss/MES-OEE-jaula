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

SELECT time, [Real] FROM (
    SELECT 
        @ShiftStart AS time,
        0 AS [Real]
    UNION ALL
    SELECT 
        TRY_CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AS time,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2)) AS [Real]
    FROM dbo.LOG_TABLA l
    WHERE l.FECHA_HORA_FIN_SEC IS NOT NULL
      AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @DashboardDate
      AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) >= DATEADD(hour, @ShiftStartHour, CAST(@DashboardDate AS DATETIME))
      AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) <= DATEADD(hour, @ShiftEndHour, CAST(@DashboardDate AS DATETIME))
) t
ORDER BY time;