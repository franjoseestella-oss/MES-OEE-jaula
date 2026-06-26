import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

def test_panel10(date_str, current_time_override=None):
    print("=" * 80)
    print(f"TESTING PANEL 10 FOR DATE: {date_str} (Current Time Override: {current_time_override})")
    print("=" * 80)
    
    # We construct the query
    # If current_time_override is provided, we set @CurrentProgressTime to it.
    override_sql = ""
    if current_time_override:
        override_sql = f"SET @CurrentProgressTime = '{current_time_override}';"
        
    sql = f"""
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '{date_str.replace("-", "")}';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
    DECLARE @PlotDate DATE = TRY_CAST(@ActiveDate AS DATE);

    -- Get timezone offset
    DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
    DECLARE @ShiftStartDT DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));
    DECLARE @ShiftEndDT DATETIME = DATEADD(hour, 15 - @UTCOffset, CAST(@PlotDate AS DATETIME));

    -- Current progress time limit
    DECLARE @CurrentProgressTime DATETIME;
    SELECT @CurrentProgressTime = CASE 
        WHEN CAST(GETDATE() AS DATE) = @PlotDate THEN GETUTCDATE()
        WHEN @PlotDate > CAST(GETDATE() AS DATE) THEN @ShiftStartDT
        ELSE @ShiftEndDT
    END;

    {override_sql}

    -- Get active reference/sequence in cycle
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

    -- Create schedule slots table
    IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
    CREATE TABLE #CalendarSlots (
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
    WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0;

    -- Map sequences using Partition By Day
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
            ROW_NUMBER() OVER (PARTITION BY fecha_montaje ORDER BY TRY_CAST(secuencia AS INT) ASC) as slot_idx_in_day
        FROM dbo.JAULA_ERP
    )
    INSERT INTO #MappedSeqs (id, secuencia, bastidor, modelo, original_date, planned_date, slot_idx, horario)
    SELECT 
        o.id,
        o.secuencia,
        o.bastidor,
        o.modelo,
        o.original_date,
        o.original_date,
        o.slot_idx_in_day,
        cs.horario
    FROM OrderedERP o
    LEFT JOIN #CalendarSlots cs ON cs.fecha = o.original_date AND cs.slot_idx_in_day = o.slot_idx_in_day;

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
        COALESCE(log.FECHA_HORA_INICIO_SEC, CASE WHEN m.bastidor = @ActiveBastidor THEN @ActiveStartDT ELSE NULL END),
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

    UPDATE s
    SET 
        s.planned_start = DATEADD(hour, -@UTCOffset, DATEADD(second, 
            CASE 
                WHEN m.slot_idx = 1 THEN 0
                ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
            END,
            DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
        )),
        s.planned_end = DATEADD(hour, -@UTCOffset, CASE 
            WHEN m.horario IS NOT NULL THEN 
                DATEADD(second, 
                    DATEDIFF(second, '07:00:00', m.horario),
                    DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
                )
            ELSE
                DATEADD(minute, 25, 
                    DATEADD(second, 
                        CASE 
                            WHEN m.slot_idx = 1 THEN 0
                            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                        END,
                        DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))
                    )
                )
        END)
    FROM #SeqsToSchedule s
    INNER JOIN #MappedSeqs m ON m.id = s.id
    LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = m.planned_date AND t_prev.slot_idx_in_day = m.slot_idx - 1;

    -- Delete future sequences that haven't started yet
    DELETE FROM #SeqsToSchedule
    WHERE planned_start > @CurrentProgressTime
      AND actual_start IS NULL;

    -- Output sequences that remain
    SELECT secuencia, bastidor, planned_start, planned_end
    FROM #SeqsToSchedule
    ORDER BY slot_idx ASC;
    """
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"Active/Planned sequences shown on timeline (Total: {len(rows)}):")
    for r in rows:
         print(f"  Seq: {r[0]} | Bastidor: {r[1]} | Planned Start: {r[2]} | Planned End: {r[3]}")

# Let's test with no overrides first
test_panel10("2026-06-29")
test_panel10("2026-06-30")

# Let's override current progress time to simulate being in the middle of a shift (e.g. 09:00:00 UTC / 11:00:00 Romance local time)
# For 2026-06-30, let's set current time to '2026-06-30 08:00:00' (UTC, Romance standard time is 10:00:00)
test_panel10("2026-06-30", current_time_override="2026-06-30 08:00:00")

cursor.close()
conn.close()
