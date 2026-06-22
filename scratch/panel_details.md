# Panel 9: Línea de Tiempo de Estados

- **Type**: state-timeline

- **GridPos**: {'h': 8, 'w': 24, 'x': 0, 'y': 20}

- **Targets count**: 1

## Target 0 (RefId: A):

**Format**: table

### SQL:

```sql
SELECT timestamp AS time, CASE state WHEN 'Running' THEN 1 WHEN 'Stopped' THEN 0 WHEN 'Setup' THEN 2 WHEN 'Micro-stop' THEN 3 WHEN 'Break' THEN 4 ELSE -1 END AS [Estado] FROM mes_machine_events WHERE machine_id = 'MAQ-01' AND timestamp >= $__timeFrom() AND timestamp <= $__timeTo() ORDER BY timestamp
```

## Options:

```json
{
  "alignValue": "left",
  "mergeValues": true,
  "showValue": "never"
}
```

--------------------------------------------------------------------------------

# Panel 10: Plan de Producción por Secuencias (Teórico vs Real)

- **Type**: state-timeline

- **GridPos**: {'h': 20, 'w': 24, 'x': 0, 'y': 28}

- **Targets count**: 1

## Target 0 (RefId: A):

**Format**: time_series

### SQL:

```sql
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

-- Get all sequences of the week
IF OBJECT_ID('tempdb..#SeqsToSchedule') IS NOT NULL DROP TABLE #SeqsToSchedule;
CREATE TABLE #SeqsToSchedule (
    id INT PRIMARY KEY,
    secuencia VARCHAR(50),
    bastidor VARCHAR(50),
    modelo VARCHAR(50),
    original_date DATE,
    completed BIT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Pendiente',
    completion_time DATETIME,
    actual_date DATE,
    scheduled_date DATE,
    slot_idx INT,
    planned_start DATETIME,
    planned_end DATETIME
);

INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, modelo, original_date, completed, status, completion_time, actual_date)
SELECT 
    erp.id,
    erp.secuencia,
    erp.bastidor,
    erp.modelo,
    TRY_CAST(erp.fecha_montaje AS DATE),
    CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
    COALESCE(log.OK_NOK, 'Pendiente'),
    log.FECHA_HORA_FIN_SEC,
    TRY_CAST(CAST(COALESCE(log.FECHA_HORA_FIN_SEC, log.FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE)
FROM dbo.JAULA_ERP erp
LEFT JOIN (
    SELECT 
        id,
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = erp.bastidor AND log.FECHA_MONTAJE = TRY_CAST(erp.fecha_montaje AS DATE) AND log.rn = 1
WHERE 
    (TRY_CAST(erp.fecha_montaje AS DATE) BETWEEN @Monday AND @Friday)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday AND log.id IS NULL)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday 
        AND log.id IS NOT NULL 
        AND TRY_CAST(CAST(COALESCE(log.FECHA_HORA_FIN_SEC, log.FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) BETWEEN @Monday AND @Friday);

-- First, any sequence that was completed is scheduled on the day it actually ran
UPDATE #SeqsToSchedule
SET scheduled_date = actual_date
WHERE completed = 1 AND actual_date IS NOT NULL;

-- Now we loop day-by-day to schedule pending sequences
DECLARE @CurrDate DATE = @Monday;
DECLARE @Today DATE = CAST(GETDATE() AS DATE);

WHILE @CurrDate <= @Friday
BEGIN
    DECLARE @Cap INT;
    SELECT @Cap = COUNT(*) FROM #WeeklyScheduleSlots WHERE fecha = @CurrDate;
    
    DECLARE @Occupied INT;
    SELECT @Occupied = COUNT(*) FROM #SeqsToSchedule WHERE scheduled_date = @CurrDate;
    
    DECLARE @Available INT = @Cap - @Occupied;
    
    IF @CurrDate >= @Today AND @Available > 0
    BEGIN
        WITH TodayPending AS (
            SELECT TOP (@Available) *
            FROM #SeqsToSchedule
            WHERE scheduled_date IS NULL
              AND original_date <= @CurrDate
            ORDER BY id ASC
        )
        UPDATE TodayPending
        SET scheduled_date = @CurrDate;
    END;
    
    SET @CurrDate = DATEADD(day, 1, @CurrDate);
END;

-- Any sequences still not scheduled are scheduled for next Monday (or Friday + 3)
UPDATE #SeqsToSchedule
SET scheduled_date = DATEADD(day, 3, @Friday)
WHERE scheduled_date IS NULL;

-- Now assign slot_idx, planned_start and planned_end
WITH OrderedScheduled AS (
    SELECT 
        id,
        scheduled_date,
        ROW_NUMBER() OVER (PARTITION BY scheduled_date ORDER BY completed DESC, id ASC) as row_idx
    FROM #SeqsToSchedule
)
UPDATE s
SET 
    s.slot_idx = os.row_idx,
    s.planned_start = DATEADD(second, 
        CASE 
            WHEN os.row_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(s.scheduled_date AS DATETIME))
    ),
    s.planned_end = DATEADD(second, 
        DATEDIFF(second, '07:00:00', COALESCE(t_curr.horario, '07:00:00')),
        DATEADD(hour, 7, CAST(s.scheduled_date AS DATETIME))
    )
FROM #SeqsToSchedule s
INNER JOIN OrderedScheduled os ON os.id = s.id
LEFT JOIN #WeeklyScheduleSlots t_curr ON t_curr.fecha = s.scheduled_date AND t_curr.slot_idx = os.row_idx
LEFT JOIN #WeeklyScheduleSlots t_prev ON t_prev.fecha = s.scheduled_date AND t_prev.slot_idx = os.row_idx - 1;

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
    WHERE s.scheduled_date = @SelectedDate
)
SELECT time, metric, value FROM (
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
    
    SELECT 
        planned_end AS time,
        secuencia AS metric,
        NULL AS value
    FROM SequenceStates
) t
ORDER BY metric ASC, time ASC;
```

## Options:

```json
{
  "alignValue": "left",
  "mergeValues": true,
  "showValue": "never"
}
```

--------------------------------------------------------------------------------
