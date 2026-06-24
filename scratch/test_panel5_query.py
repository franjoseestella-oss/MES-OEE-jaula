import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

def inspect():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    sql = """
    SET NOCOUNT ON;
    DECLARE @ActiveDate VARCHAR(8) = '20260624';
    DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);
    DECLARE @Monday DATE = DATEADD(wk, DATEDIFF(wk, 0, @SelectedDate), 0);
    DECLARE @Friday DATE = DATEADD(day, 4, @Monday);

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

    -- Now assign planned times ONLY if planned_date is within the current week
    SELECT 
        ROW_NUMBER() OVER (ORDER BY COALESCE(s.planned_date, '1900-01-01') ASC, s.slot_idx ASC, s.secuencia ASC) AS [ID],
        s.secuencia AS [Secuencia],
        s.bastidor AS [Bastidor],
        s.modelo AS [Modelo],
        COALESCE(CONVERT(varchar(10), s.planned_date, 103), '') AS [Fecha Montaje],
        -- Planned Times are ONLY shown if planned_date falls within the active week
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
        END AS [Inicio Planificado],
        CASE 
            WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
                CONVERT(varchar(8), 
                    DATEADD(second, 
                        DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                        DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                    ), 
                    108
                )
            ELSE ''
        END AS [Fin Planificado],
        CONVERT(varchar(8), CAST(s.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
        CONVERT(varchar(8), CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
        CASE 
            WHEN s.FECHA_HORA_FIN_SEC IS NULL THEN '-'
            ELSE 
                -- Deviation is only calculated if planned times exist
                CASE 
                    WHEN s.planned_date BETWEEN @Monday AND @Friday THEN
                        CASE 
                            WHEN DATEDIFF(minute, 
                                DATEADD(second, 
                                    DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                    DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                                ), 
                                CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                            ) > 0 
                                THEN '+' + CAST(DATEDIFF(minute, 
                                    DATEADD(second, 
                                        DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                        DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                                    ), 
                                    CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                                ) AS VARCHAR) + ' min'
                            ELSE 
                                CAST(DATEDIFF(minute, 
                                    DATEADD(second, 
                                        DATEDIFF(second, '07:00:00', COALESCE(s.horario, '07:00:00')),
                                        DATEADD(hour, 7, CAST(s.planned_date AS DATETIME))
                                    ), 
                                    CAST(CAST(s.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)
                                ) AS VARCHAR) + ' min'
                        END
                    ELSE '-'
                END
        END AS [Desviación],
        COALESCE(s.log_status, 'Pendiente') AS [Estado]
    FROM #SeqsWithLog s
    LEFT JOIN #CalendarSlots t_prev ON t_prev.fecha = s.planned_date AND t_prev.slot_idx_in_day = s.slot_idx - 1
    WHERE 
        -- Show sequences planned for this week
        (s.planned_date BETWEEN @Monday AND @Friday)
        -- OR sequences planned for the past (or not planned / < 227) that are either NOT completed, or completed during this week
        OR (
            (s.planned_date < @Monday OR s.planned_date IS NULL)
            AND (
                s.log_status IS NULL 
                OR s.log_status = 'NOK' 
                -- Completed this week
                OR CAST(s.log_fecha_montaje AS DATE) BETWEEN @Monday AND @Friday
            )
        )
    ORDER BY COALESCE(s.planned_date, '1900-01-01') ASC, s.slot_idx ASC, s.secuencia ASC;
    """
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    # Print columns
    print([d[0] for d in cursor.description])
    # Print all rows
    for r in rows:
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
