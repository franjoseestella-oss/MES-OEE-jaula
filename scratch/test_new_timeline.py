import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = """
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '20260629';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
    DECLARE @timeFrom DATETIME2 = '2026-06-29T05:00:00Z'; 
    DECLARE @PlotDate DATE = CAST(CAST(@timeFrom AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE);
    
    DECLARE @ShiftStartHour INT, @ShiftEndHour INT;
    DECLARE @ShiftStartStr VARCHAR(8);
    
    SELECT 
        @ShiftStartHour = DATEPART(hour, hora_inicio_jornada),
        @ShiftEndHour = DATEPART(hour, hora_fin_jornada),
        @ShiftStartStr = CAST(hora_inicio_jornada AS VARCHAR(8))
    FROM dbo.TURNO_TRABAJO;
    
    DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
    DECLARE @ShiftStartDT DATETIME = DATEADD(hour, @ShiftStartHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
    DECLARE @ShiftEndDT DATETIME = DATEADD(hour, @ShiftEndHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
    
    DECLARE @CurrentProgressTime DATETIME = GETUTCDATE();
    
    DECLARE @ActiveBastidor VARCHAR(50);
    DECLARE @ActiveStartDT DATETIME;
    
    SELECT TOP 1 
        @ActiveBastidor = NBASTIDOR,
        @ActiveStartDT = DATEADD(hour, -@UTCOffset, TRY_CONVERT(DATETIME, 
            SUBSTRING(FECHA_INICIO_CICLO, 13, 4) + '-' + 
            SUBSTRING(FECHA_INICIO_CICLO, 10, 2) + '-' + 
            SUBSTRING(FECHA_INICIO_CICLO, 7, 2) + 'T' + 
            SUBSTRING(FECHA_INICIO_CICLO, 1, 5) + ':00'
        ))
    FROM dbo.REFERENCIA_EN_CICLO
    WHERE LEN(FECHA_INICIO_CICLO) >= 16;
    
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
        planned_end DATETIME,
        planned_date DATE,
        slot_idx INT,
        actual_start DATETIME,
        actual_end DATETIME
    );
    
    INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, modelo, completed, status, completion_time, planned_date, slot_idx, actual_start, actual_end)
    SELECT 
        m.id,
        m.secuencia,
        m.bastidor,
        m.modelo,
        CASE WHEN log.id IS NOT NULL THEN 1 ELSE 0 END,
        COALESCE(log.OK_NOK, 'Pendiente'),
        log.FECHA_HORA_FIN_SEC,
        m.planned_date,
        m.slot_idx,
        COALESCE(
            log.FECHA_HORA_INICIO_SEC,
            (SELECT MIN(timestamp) FROM dbo.mes_machine_events WHERE secuencia_id = m.secuencia AND state = 'SECUENCIA_INICIADA' AND timestamp >= @ShiftStartDT),
            CASE WHEN m.bastidor = @ActiveBastidor THEN @ActiveStartDT ELSE NULL END
        ),
        log.FECHA_HORA_FIN_SEC
    FROM #MappedSeqs m
    LEFT JOIN (
        SELECT 
            id,
            NBASTIDOR,
            FECHA_MONTAJE,
            OK_NOK,
            TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) AS FECHA_HORA_INICIO_SEC,
            TRY_CAST(FECHA_HORA_FIN_SEC AS DATETIME2) AS FECHA_HORA_FIN_SEC,
            ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
        FROM dbo.LOG_TABLA
    ) log ON log.NBASTIDOR = m.bastidor AND log.rn = 1
    WHERE m.planned_date = @SelectedDate;

    -- Update actual_end for started but incomplete sequences (using next SEQUENCE_INICIADA start)
    UPDATE s
    SET s.actual_end = (
        SELECT MIN(timestamp) 
        FROM dbo.mes_machine_events 
        WHERE state = 'SECUENCIA_INICIADA' 
          AND timestamp > s.actual_start 
          AND secuencia_id != s.secuencia
    )
    FROM #SeqsToSchedule s
    WHERE s.actual_start IS NOT NULL AND s.actual_end IS NULL;

    WITH PlannedTimes AS (
        SELECT 
            s.id,
            DATEADD(minute, (s.slot_idx - 1) * 25 + 15, CAST(@ShiftStartDT AS DATETIME)) AS planned_start,
            DATEADD(minute, s.slot_idx * 25 + 15, CAST(@ShiftStartDT AS DATETIME)) AS planned_end
        FROM #SeqsToSchedule s
    )
    UPDATE s
    SET s.planned_start = p.planned_start,
        s.planned_end = p.planned_end
    FROM #SeqsToSchedule s
    JOIN PlannedTimes p ON s.id = p.id;
    
    DECLARE @ActiveSlotIdx INT = NULL;
    IF @ActiveBastidor IS NOT NULL
    BEGIN
        SELECT TOP 1 @ActiveSlotIdx = slot_idx
        FROM #SeqsToSchedule
        WHERE bastidor = @ActiveBastidor;
    END;
    
    DECLARE @TheoreticalActiveSlotIdx INT = NULL;
    SELECT TOP 1 @TheoreticalActiveSlotIdx = slot_idx
    FROM #SeqsToSchedule
    WHERE completed = 0
    ORDER BY slot_idx ASC;

    WITH DistinctTimestamps AS (
        SELECT @ShiftStartDT AS t
        UNION
        SELECT @ShiftEndDT AS t
        UNION
        SELECT DISTINCT planned_start FROM #SeqsToSchedule
        UNION
        SELECT DISTINCT planned_end FROM #SeqsToSchedule
        UNION
        SELECT DISTINCT actual_start FROM #SeqsToSchedule WHERE actual_start IS NOT NULL
        UNION
        SELECT DISTINCT actual_end FROM #SeqsToSchedule WHERE actual_end IS NOT NULL
        UNION
        SELECT DISTINCT timestamp FROM dbo.mes_machine_events 
        WHERE timestamp >= @ShiftStartDT AND timestamp <= @ShiftEndDT
    ),
    OrderedTimestamps AS (
        SELECT t, ROW_NUMBER() OVER (ORDER BY t ASC) AS rn
        FROM DistinctTimestamps
        WHERE t >= @ShiftStartDT AND t <= @ShiftEndDT
    ),
    TimeIntervals AS (
        SELECT 
            t1.t AS t_start, 
            t2.t AS t_end
        FROM OrderedTimestamps t1
        JOIN OrderedTimestamps t2 ON t1.rn = t2.rn - 1
    ),
    AlarmIntervals AS (
        SELECT 
            t_start AS alarm_start,
            t_end AS alarm_end
        FROM TimeIntervals ti
        WHERE EXISTS (
            SELECT 1 FROM dbo.mes_machine_events ev
            WHERE ev.timestamp <= ti.t_start
              AND ev.timestamp >= DATEADD(minute, -10, ti.t_start)
              AND ev.state = 'Alarm'
        )
    ),
    FlatTimeline AS (
        SELECT 
            ti.t_start,
            ti.t_end,
            s.secuencia,
            s.bastidor,
            s.modelo,
            s.slot_idx,
            s.planned_start,
            s.planned_end,
            s.actual_start,
            s.actual_end,
            CASE
                WHEN s.actual_start IS NOT NULL AND ti.t_start >= s.actual_start AND (s.actual_end IS NULL OR ti.t_start < s.actual_end) THEN
                    CASE 
                        WHEN ti.t_start < s.planned_start OR ti.t_start >= s.planned_end THEN 'Exceso de tiempo'
                        ELSE 'En proceso'
                    END
                WHEN ti.t_start >= s.planned_start AND ti.t_start < s.planned_end THEN 'Esperando máquina'
                ELSE NULL
            END AS state_val
        FROM TimeIntervals ti
        CROSS JOIN #SeqsToSchedule s
    ),
    FilteredTimeline AS (
        SELECT 
            t_start,
            t_end,
            secuencia + ' ' + bastidor AS metric,
            CASE 
                WHEN state_val IS NULL THEN NULL
                WHEN slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                     AND EXISTS (
                         SELECT 1 FROM AlarmIntervals a 
                         WHERE t_start >= a.alarm_start AND t_start < a.alarm_end
                     ) THEN 'Alarma'
                ELSE state_val
            END AS val
        FROM FlatTimeline
    ),
    FilteredTimelineWithLead AS (
        SELECT 
            t_start,
            metric,
            val,
            LAG(val) OVER (PARTITION BY metric ORDER BY t_start ASC) as prev_val
        FROM FilteredTimeline
    ),
    ChangesOnly AS (
        SELECT 
            t_start,
            metric,
            val
        FROM FilteredTimelineWithLead
        WHERE val IS DISTINCT FROM prev_val
    )
    SELECT 
        DATEADD(hour, @UTCOffset, t_start) AS [time],
        metric,
        val
    FROM ChangesOnly
    WHERE metric LIKE '%0273%' OR metric LIKE '%0261%'
    ORDER BY metric, [time] ASC;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    for r in rows:
        print(f"Time: {r[0]}, Metric: {r[1]}, Value: {r[2]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
