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

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

-- Get shift start and end times
DECLARE @ShiftStart TIME, @ShiftEnd TIME;
SELECT TOP 1 
    @ShiftStart = CAST(hora_inicio_jornada AS TIME),
    @ShiftEnd = CAST(hora_fin_jornada AS TIME)
FROM dbo.TURNO_TRABAJO;

IF @ShiftStart IS NULL SET @ShiftStart = '07:00:00';
IF @ShiftEnd IS NULL SET @ShiftEnd = '15:00:00';

DECLARE @ShiftStartDT DATETIME = DATEADD(second, DATEDIFF(second, '00:00:00', @ShiftStart), CAST(@SelectedDate AS DATETIME));
DECLARE @ShiftEndDT DATETIME = DATEADD(second, DATEDIFF(second, '00:00:00', @ShiftEnd), CAST(@SelectedDate AS DATETIME));

-- Get capacity for the selected day
DECLARE @DayCap DECIMAL(4,1);
SELECT @DayCap = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @SelectedDate;

IF @DayCap IS NULL SET @DayCap = 18.0;

-- Create schedule slots table for the day
IF OBJECT_ID('tempdb..#DayScheduleSlots') IS NOT NULL DROP TABLE #DayScheduleSlots;
CREATE TABLE #DayScheduleSlots (
    slot_idx INT PRIMARY KEY,
    horario TIME
);

IF @DayCap = 18.0
BEGIN
    INSERT INTO #DayScheduleSlots (slot_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END
ELSE IF @DayCap = 19.0
BEGIN
    INSERT INTO #DayScheduleSlots (slot_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_19;
END
ELSE IF @DayCap = 18.5
BEGIN
    DECLARE @Cnt185 INT = 0;
    SELECT @Cnt185 = COUNT(*)
    FROM dbo.CALENDARIO_LABORAL
    WHERE Laborable = 1 
      AND Cant_A_Fabricar = 18.5 
      AND Fecha <= @SelectedDate;

    IF @Cnt185 > 0 AND @Cnt185 % 2 = 0
    BEGIN
        INSERT INTO #DayScheduleSlots (slot_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 20 AND 38;
    END
    ELSE
    BEGIN
        INSERT INTO #DayScheduleSlots (slot_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 1 AND 19;
    END
END
ELSE
BEGIN
    INSERT INTO #DayScheduleSlots (slot_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END;

-- Get only the sequences scheduled for the selected day in JAULA_ERP (fecha_montaje = @ActiveDate)
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
    erp.id,
    erp.secuencia,
    erp.bastidor,
    erp.modelo,
    CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
    COALESCE(log.OK_NOK, 'Pendiente'),
    log.FECHA_HORA_FIN_SEC
FROM dbo.JAULA_ERP erp
LEFT JOIN (
    SELECT 
        id,
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = erp.bastidor AND log.FECHA_MONTAJE = TRY_CAST(erp.fecha_montaje AS DATE) AND log.rn = 1
WHERE erp.fecha_montaje = @ActiveDate;

-- Assign planned start and end times based on slot indices ordered by sequence ID
WITH OrderedScheduled AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY id ASC) as row_idx
    FROM #SeqsToSchedule
)
UPDATE s
SET 
    s.planned_start = DATEADD(second, 
        CASE 
            WHEN os.row_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(@SelectedDate AS DATETIME))
    ),
    s.planned_end = CASE 
        WHEN t_curr.horario IS NOT NULL THEN 
            DATEADD(second, 
                DATEDIFF(second, '07:00:00', t_curr.horario),
                DATEADD(hour, 7, CAST(@SelectedDate AS DATETIME))
            )
        ELSE
            DATEADD(minute, 25, 
                DATEADD(second, 
                    CASE 
                        WHEN os.row_idx = 1 THEN 0
                        ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                    END,
                    DATEADD(hour, 7, CAST(@SelectedDate AS DATETIME))
                )
            )
    END
FROM #SeqsToSchedule s
INNER JOIN OrderedScheduled os ON os.id = s.id
LEFT JOIN #DayScheduleSlots t_curr ON t_curr.slot_idx = os.row_idx
LEFT JOIN #DayScheduleSlots t_prev ON t_prev.slot_idx = os.row_idx - 1;

-- Output for timeline
WITH SequenceStates AS (
    SELECT 
        secuencia,
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
        secuencia AS metric,
        NULL AS value
    FROM SequenceStates
    WHERE planned_start > @ShiftStartDT
    
    UNION ALL
    
    -- Sequence planned start with its state
    SELECT 
        planned_start AS time,
        secuencia AS metric,
        CASE COALESCE(latest_state, 'Idle')
            WHEN 'Execute' THEN 'EN_PROCESO'
            WHEN 'Starting' THEN 'SECUENCIA_INICIADA'
            WHEN 'Running' THEN 'EN_PROCESO'
            WHEN 'Idle' THEN 'EN_ESPERA'
            WHEN 'Held' THEN 'PAUSADA'
            WHEN 'Complete' THEN 'FINALIZADA'
            WHEN 'Stopped' THEN 'FINALIZADA'
            WHEN 'Aborted' THEN 'ERROR'
            WHEN 'Aborting' THEN 'ERROR'
            WHEN 'EN_PROCESO' THEN 'EN_PROCESO'
            WHEN 'SECUENCIA_INICIADA' THEN 'SECUENCIA_INICIADA'
            WHEN 'EN_ESPERA' THEN 'EN_ESPERA'
            WHEN 'PAUSADA' THEN 'PAUSADA'
            WHEN 'FINALIZADA' THEN 'FINALIZADA'
            WHEN 'ERROR' THEN 'ERROR'
            ELSE 'EN_ESPERA'
        END AS value
    FROM SequenceStates
    
    UNION ALL
    
    -- Sequence planned end to terminate the block
    SELECT 
        planned_end AS time,
        secuencia AS metric,
        NULL AS value
    FROM SequenceStates
    
    UNION ALL
    
    -- Shift end boundary to force horizontal axis range
    SELECT 
        @ShiftEndDT AS time,
        secuencia AS metric,
        NULL AS value
    FROM SequenceStates
    WHERE planned_end < @ShiftEndDT
) t
ORDER BY metric ASC, time ASC;