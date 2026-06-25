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

    SELECT 
        m.secuencia,
        m.bastidor,
        m.planned_date,
        m.slot_idx,
        m.horario,
        l.FECHA_HORA_INICIO_SEC,
        l.FECHA_HORA_FIN_SEC,
        c.FECHA_INICIO_CICLO AS active_cycle_start
    FROM #MappedSeqs m
    LEFT JOIN dbo.LOG_TABLA l ON l.NBASTIDOR = m.bastidor
    LEFT JOIN dbo.REFERENCIA_EN_CICLO c ON c.NBASTIDOR = m.bastidor
    WHERE m.planned_date = @SelectedDate
    ORDER BY m.slot_idx ASC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    for r in rows:
        print(f"Seq={r[0]}, Bastidor={r[1]}, Slot={r[3]}, Horario={r[4]}, Inicio={r[5]}, Fin={r[6]}, ActiveStart={r[7]}")
except Exception as e:
    print("Error:", e)
