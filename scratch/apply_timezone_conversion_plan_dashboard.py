import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

# Change timezone to browser
data["timezone"] = "browser"

# Panel 10 (Timeline) SQL Query
new_panel10_sql = """DECLARE @ActiveDate VARCHAR(8);
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
DECLARE @PlotDate DATE = CAST($__timeFrom() AS DATE);

-- Get shift start and end times
DECLARE @ShiftStart TIME, @ShiftEnd TIME;
SELECT TOP 1 
    @ShiftStart = CAST(hora_inicio_jornada AS TIME),
    @ShiftEnd = CAST(hora_fin_jornada AS TIME)
FROM dbo.TURNO_TRABAJO;

IF @ShiftStart IS NULL SET @ShiftStart = '07:00:00';
IF @ShiftEnd IS NULL SET @ShiftEnd = '15:00:00';

-- Timezone offset calculation to convert database local time to UTC for Grafana (which will show browser time)
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());

DECLARE @ShiftStartDT DATETIME = DATEADD(hour, -@UTCOffset, DATEADD(second, DATEDIFF(second, '00:00:00', @ShiftStart), CAST(@PlotDate AS DATETIME)));
DECLARE @ShiftEndDT DATETIME = DATEADD(hour, -@UTCOffset, DATEADD(second, DATEDIFF(second, '00:00:00', @ShiftEnd), CAST(@PlotDate AS DATETIME)));

-- Determine current progress time to auto-fill as time progresses (in UTC)
DECLARE @CurrentProgressTime DATETIME;
IF @SelectedDate = CAST(GETDATE() AS DATE)
BEGIN
    SET @CurrentProgressTime = GETUTCDATE();
END
ELSE IF @SelectedDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @CurrentProgressTime = @ShiftStartDT;
END
ELSE
BEGIN
    SET @CurrentProgressTime = @ShiftEndDT;
END;

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

-- Assign planned start and end times in UTC based on slot indices ordered by sequence ID
WITH OrderedScheduled AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY id ASC) as row_idx
    FROM #SeqsToSchedule
)
UPDATE s
SET 
    s.planned_start = DATEADD(hour, -@UTCOffset, DATEADD(second, 
        CASE 
            WHEN os.row_idx = 1 THEN 0
            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
        END,
        DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
    )),
    s.planned_end = DATEADD(hour, -@UTCOffset, CASE 
        WHEN t_curr.horario IS NOT NULL THEN 
            DATEADD(second, 
                DATEDIFF(second, '07:00:00', t_curr.horario),
                DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
            )
        ELSE
            DATEADD(minute, 25, 
                DATEADD(second, 
                    CASE 
                        WHEN os.row_idx = 1 THEN 0
                        ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                    END,
                    DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
                )
            )
    END)
FROM #SeqsToSchedule s
INNER JOIN OrderedScheduled os ON os.id = s.id
LEFT JOIN #DayScheduleSlots t_curr ON t_curr.slot_idx = os.row_idx
LEFT JOIN #DayScheduleSlots t_prev ON t_prev.slot_idx = os.row_idx - 1;

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
ORDER BY metric ASC, time ASC;"""

# Panel 4 Target A (Theoretical evolution) SQL Query
new_panel4_a_sql = """DECLARE @ActiveDate VARCHAR(8);
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
ORDER BY time;"""

# Panel 4 Target B (Real evolution) SQL Query
new_panel4_b_sql = """DECLARE @ActiveDate VARCHAR(8);
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
DECLARE @PlotDate DATE = CAST($__timeFrom() AS DATE);

-- Get timezone offset
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15 - @UTCOffset, CAST(@PlotDate AS DATETIME));

DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @DashboardDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

DECLARE @N INT = CEILING(@UnidadesAFabricar);

DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME))
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
        DATEADD(hour, -@UTCOffset, TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS time,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS [Real]
    FROM Today_Seqs t
    INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
    WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME))
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME))
      AND l.OK_NOK = 'OK'
) t
ORDER BY time;"""

# Apply the updates
for panel in data.get("panels", []):
    pid = panel.get("id")
    if pid == 10:
        panel["targets"][0]["rawSql"] = new_panel10_sql
    elif pid == 4:
        for t in panel["targets"]:
            if t.get("refId") == "A":
                t["rawSql"] = new_panel4_a_sql
            elif t.get("refId") == "B":
                t["rawSql"] = new_panel4_b_sql

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Successfully configured plan_dashboard.json timezone to 'browser' and updated queries for UTC compatibility.")
