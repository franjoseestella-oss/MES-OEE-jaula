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
    DECLARE @ActiveDate VARCHAR(8) = '20260625';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

    -- Create weekly schedule slots table
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

    -- Get completion status from log
    IF OBJECT_ID('tempdb..#SeqsWithLog') IS NOT NULL DROP TABLE #SeqsWithLog;
    SELECT 
        m.id,
        m.secuencia,
        m.bastidor,
        m.modelo,
        m.original_date,
        m.planned_date,
        m.slot_idx,
        m.horario,
        l.OK_NOK AS log_status,
        l.FECHA_MONTAJE AS log_fecha_montaje,
        l.FECHA_HORA_INICIO_SEC,
        l.FECHA_HORA_FIN_SEC
    INTO #SeqsWithLog
    FROM #MappedSeqs m
    LEFT JOIN (
        SELECT 
            id,
            NBASTIDOR,
            FECHA_MONTAJE,
            OK_NOK,
            FECHA_HORA_INICIO_SEC,
            FECHA_HORA_FIN_SEC,
            ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
        FROM dbo.LOG_TABLA
    ) l ON l.NBASTIDOR = m.bastidor AND l.rn = 1;

    -- Now assign planned times
    SELECT 
        s.secuencia AS [Secuencia],
        s.bastidor AS [Bastidor],
        CASE 
            WHEN s.FECHA_HORA_FIN_SEC IS NOT NULL THEN s.log_status
            WHEN active.id IS NOT NULL OR (s.FECHA_HORA_INICIO_SEC IS NOT NULL AND s.FECHA_HORA_FIN_SEC IS NULL) THEN 'Procesando'
            ELSE 'Pendiente'
        END AS [Estado]
    FROM #SeqsWithLog s
    LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = s.planned_date AND t_prev.slot_idx_in_day = s.slot_idx - 1
    LEFT JOIN dbo.REFERENCIA_EN_CICLO active ON active.NBASTIDOR = s.bastidor
    WHERE 
        s.planned_date = @SelectedDate
    ORDER BY s.slot_idx ASC, s.secuencia ASC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print("Sequence statuses for today:")
    for r in rows:
        print(f"Secuencia={r[0]}, Bastidor={r[1]}, Estado={r[2]}")
        
except Exception as e:
    print("Error:", e)
