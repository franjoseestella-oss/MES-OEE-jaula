import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = """
    SET NOCOUNT ON;
    DECLARE @UTCOffset INT = 2;
    DECLARE @SelectedDate DATE = '2026-06-25';
    DECLARE @PlotDate DATE = '2026-06-25';
    DECLARE @ShiftStartDT DATETIME = DATEADD(hour, 5, CAST(@PlotDate AS DATETIME)); -- 07:00 local (05:00 UTC)
    DECLARE @ShiftEndDT DATETIME = DATEADD(hour, 13, CAST(@PlotDate AS DATETIME)); -- 15:00 local (13:00 UTC)
    DECLARE @CurrentProgressTime DATETIME = DATEADD(hour, -@UTCOffset, GETDATE());

    -- Create weekly schedule slots table
    IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
    CREATE TABLE #CalendarSlots (
        global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
        fecha DATE,
        slot_idx_in_day INT,
        horario TIME
    );

    WITH CalendarBase AS (
        SELECT Fecha, Laborable, Cant_A_Fabricar,
            SUM(CASE WHEN Cant_A_Fabricar = 18.5 THEN 1 ELSE 0 END) OVER (ORDER BY Fecha ASC) AS Count185
        FROM dbo.CALENDARIO_LABORAL
        WHERE Fecha >= '2026-06-24'
    )
    INSERT INTO #CalendarSlots (fecha, slot_idx_in_day, horario)
    SELECT cb.Fecha, s.seq_idx, s.horario
    FROM CalendarBase cb
    CROSS APPLY (
        SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx, horario
        FROM dbo.HHSS_18
        WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    ) s
    WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
    ORDER BY cb.Fecha ASC, s.seq_idx ASC;

    -- Map sequences starting from 227
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
        SELECT id, secuencia, bastidor, modelo, TRY_CAST(fecha_montaje AS DATE) AS original_date,
            ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
        FROM dbo.JAULA_ERP
        WHERE TRY_CAST(secuencia AS INT) >= 227
    )
    INSERT INTO #MappedSeqs (id, secuencia, bastidor, modelo, original_date, planned_date, slot_idx, horario)
    SELECT o.id, o.secuencia, o.bastidor, o.modelo, o.original_date, cs.fecha, cs.slot_idx_in_day, cs.horario
    FROM OrderedERP o
    LEFT JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

    -- SeqsToSchedule
    IF OBJECT_ID('tempdb..#SeqsToSchedule') IS NOT NULL DROP TABLE #SeqsToSchedule;
    CREATE TABLE #SeqsToSchedule (
        id INT PRIMARY KEY,
        secuencia VARCHAR(50),
        bastidor VARCHAR(50),
        planned_start DATETIME,
        planned_end DATETIME,
        actual_start DATETIME,
        actual_end DATETIME
    );

    INSERT INTO #SeqsToSchedule (id, secuencia, bastidor, planned_start, planned_end, actual_start, actual_end)
    SELECT 
        m.id, m.secuencia, m.bastidor,
        DATEADD(hour, -@UTCOffset, DATEADD(hour, 7, CAST(@PlotDate AS DATETIME))), -- 07:00 local (05:00 UTC)
        DATEADD(hour, -@UTCOffset, DATEADD(minute, 25, DATEADD(hour, 7, CAST(@PlotDate AS DATETIME)))), -- 07:25 local (05:25 UTC)
        NULL, NULL
    FROM #MappedSeqs m
    WHERE m.secuencia = '0271';

    SELECT 
        secuencia,
        planned_start,
        planned_end,
        @CurrentProgressTime AS CurrentProgressTime,
        CASE 
            WHEN planned_start >= @CurrentProgressTime THEN planned_start
            ELSE
                CASE 
                    WHEN planned_end > @CurrentProgressTime THEN @CurrentProgressTime
                    ELSE planned_end
                END
        END AS computed_upper_limit
    FROM #SeqsToSchedule;
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    print("Row:", row)
    
except Exception as e:
    print("Error:", e)
