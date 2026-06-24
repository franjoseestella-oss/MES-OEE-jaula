import json
import os

def main():
    filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find the panel with title "LISTADO DE SECUENCIAS (PLAN vs REAL)"
    found = False
    for panel in data.get("panels", []):
        if panel.get("title") == "LISTADO DE SECUENCIAS (PLAN vs REAL)":
            targets = panel.get("targets", [])
            if targets:
                new_query = """DECLARE @ActiveDate VARCHAR(8);
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

-- Get all sequences of the week + past uncompleted ones
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
    CASE WHEN log.id IS NOT NULL AND log.OK_NOK = 'OK' THEN 1 ELSE 0 END,
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
        TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME) AS FECHA_HORA_INICIO_SEC,
        TRY_CAST(FECHA_HORA_FIN_SEC AS DATETIME) AS FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = erp.bastidor AND log.FECHA_MONTAJE = TRY_CAST(erp.fecha_montaje AS DATE) AND log.rn = 1
WHERE 
    (TRY_CAST(erp.fecha_montaje AS DATE) BETWEEN @Monday AND @Friday)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday 
        AND log.id IS NOT NULL 
        AND TRY_CAST(CAST(COALESCE(log.FECHA_HORA_FIN_SEC, log.FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) BETWEEN @Monday AND @Friday)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday 
        AND (log.id IS NULL OR log.OK_NOK = 'NOK'));

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

-- Output
SELECT 
    ROW_NUMBER() OVER (ORDER BY s.scheduled_date ASC, s.slot_idx ASC) AS [ID],
    s.secuencia AS [Secuencia],
    s.bastidor AS [Bastidor],
    s.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), s.scheduled_date, 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), s.planned_start, 108) AS [Inicio Planificado],
    CONVERT(varchar(8), s.planned_end, 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN l.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, s.planned_end, CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, s.planned_end, CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, s.planned_end, CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM #SeqsToSchedule s
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
) l ON l.NBASTIDOR = s.bastidor AND l.FECHA_MONTAJE = s.original_date AND l.rn = 1
ORDER BY s.scheduled_date ASC, s.slot_idx ASC;"""
                targets[0]["rawSql"] = new_query
                found = True
                print("Successfully updated target rawSql.")
            break

    if not found:
        print("Error: LISTADO DE SECUENCIAS (PLAN vs REAL) panel not found.")
        return

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully wrote updated plan_dashboard.json.")

if __name__ == "__main__":
    main()
