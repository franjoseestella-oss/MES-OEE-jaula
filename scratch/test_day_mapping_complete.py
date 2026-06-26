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

def test_queries_for_date(date_str):
    print("=" * 80)
    print(f"TESTING FOR DATE: {date_str}")
    print("=" * 80)
    
    # 1. Test Panel 1 Query (Theoretical count)
    p1_sql = f"""
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '{date_str.replace("-", "")}';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

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

    WITH OrderedERP AS (
        SELECT 
            id,
            TRY_CAST(fecha_montaje AS DATE) AS original_date,
            ROW_NUMBER() OVER (PARTITION BY fecha_montaje ORDER BY TRY_CAST(secuencia AS INT) ASC) as slot_idx_in_day
        FROM dbo.JAULA_ERP
    )
    SELECT COUNT(*) AS [Teórico]
    FROM OrderedERP
    WHERE original_date = @SelectedDate;
    """
    cursor.execute(p1_sql)
    teorico = cursor.fetchone()[0]
    print(f"Panel 1 (Teórico): {teorico}")
    
    # 2. Test Panel 3 Query (Desviacion)
    p3_sql = f"""
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '{date_str.replace("-", "")}';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

    WITH OrderedERP AS (
        SELECT 
            id,
            TRY_CAST(fecha_montaje AS DATE) AS original_date,
            ROW_NUMBER() OVER (PARTITION BY fecha_montaje ORDER BY TRY_CAST(secuencia AS INT) ASC) as slot_idx_in_day
        FROM dbo.JAULA_ERP
    )
    SELECT COUNT(*)
    FROM OrderedERP
    WHERE original_date = @SelectedDate;
    """
    cursor.execute(p3_sql)
    teorico_p3 = cursor.fetchone()[0]
    
    p3_real_sql = f"""
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '{date_str.replace("-", "")}';
    SELECT COUNT(DISTINCT log.NBASTIDOR)
    FROM dbo.LOG_TABLA log
    INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
    WHERE log.FECHA_MONTAJE = TRY_CAST(@ActiveDate AS DATE);
    """
    cursor.execute(p3_real_sql)
    real_p3 = cursor.fetchone()[0]
    print(f"Panel 3 (Real): {real_p3} | Desviación: {real_p3 - teorico_p3}")

    # 3. Test Panel 5 Query (Listado de secuencias)
    p5_sql = f"""
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '{date_str.replace("-", "")}';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
    DECLARE @Monday DATE = DATEADD(wk, DATEDIFF(wk, 0, @SelectedDate), 0);
    DECLARE @Friday DATE = DATEADD(day, 4, @Monday);

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

    SELECT TOP 5
        s.secuencia,
        s.bastidor,
        COALESCE(CONVERT(varchar(10), s.planned_date, 103), '') AS planned_date_str,
        CASE 
            WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
                CONVERT(varchar(8), 
                    DATEADD(second, 
                        CASE 
                            WHEN s.slot_idx = 1 THEN 0
                            ELSE DATEDIFF(second, '07:00:00', COALESCE(t_prev.horario, '07:00:00'))
                        END,
                        DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                    ), 
                    108
                )
            ELSE ''
        END AS start_plan,
        COALESCE(s.log_status, 'Pendiente') AS status
    FROM #SeqsWithLog s
    LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = s.planned_date AND t_prev.slot_idx_in_day = s.slot_idx - 1
    WHERE 
        (s.planned_date BETWEEN @Monday AND @Friday)
        OR (
            (s.planned_date < @Monday OR s.planned_date IS NULL)
            AND (
                s.log_status IS NULL 
                OR s.log_status = 'NOK' 
                OR CAST(s.log_fecha_montaje AS DATE) BETWEEN @Monday AND @Friday
            )
        )
    ORDER BY COALESCE(s.planned_date, '1900-01-01') ASC, s.slot_idx ASC, s.secuencia ASC;
    """
    cursor.execute(p5_sql)
    p5_rows = cursor.fetchall()
    print("Panel 5 (Sample of 5 rows):")
    for r in p5_rows:
        print(f"  Seq: {r[0]} | Bastidor: {r[1]} | Planned Date: {r[2]} | Start Plan: {r[3]} | Status: {r[4]}")

test_queries_for_date("2026-06-29")
test_queries_for_date("2026-06-30")
test_queries_for_date("2026-07-01")
test_queries_for_date("2026-07-24")

cursor.close()
conn.close()
