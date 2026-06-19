import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Test with a date in June, e.g. 2026-06-15
test_date = '2026-06-15'

query = """
SET NOCOUNT ON;
DECLARE @ActiveDate DATE = ?;

-- 1. Determine unidades a fabricar for the day
DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @ActiveDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

-- 2. Determine number of sequences to plan today
DECLARE @N INT = CEILING(@UnidadesAFabricar);

-- 3. Check odd/even of 18.5 days to select appropriate set from HHSS_18_5
DECLARE @Count185 INT = 0;
SELECT @Count185 = COUNT(*)
FROM dbo.CALENDARIO_LABORAL
WHERE Laborable = 1 
  AND Cant_A_Fabricar = 18.5 
  AND Fecha <= @ActiveDate;

DECLARE @UseSecondSet185 BIT = 0;
IF @Count185 > 0 AND @Count185 % 2 = 0
    SET @UseSecondSet185 = 1;

-- 4. Find the last completed sequence of the previous day
DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < DATEADD(hour, 7, CAST(@ActiveDate AS DATETIME))
  AND log.OK_NOK = 'OK'
ORDER BY erp.id DESC;

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP
    WHERE fecha_montaje = CONVERT(varchar(8), @ActiveDate, 112);
END

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP;
END

-- 5. Create temporary table for shift schedule times
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
        CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado],
        CASE 
            WHEN s.seq_idx = 1 THEN CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' 07:00:00') AS DATETIME)
            ELSE CAST(CONCAT(CONVERT(VARCHAR(10), @ActiveDate, 120), ' ', CONVERT(VARCHAR(8), prev.horario, 108)) AS DATETIME)
        END AS [Inicio Planificado]
    FROM #ShiftSchedule s
    LEFT JOIN #ShiftSchedule prev ON prev.seq_idx = s.seq_idx - 1
),
Today_Seqs AS (
    -- The last completed sequence of the previous day (row 0)
    SELECT 
        j.id,
        j.secuencia,
        j.bastidor,
        j.modelo,
        j.fecha_montaje,
        0 AS seq_idx
    FROM dbo.JAULA_ERP j
    WHERE j.id = @LastCompletedID

    UNION ALL

    -- Today's planned sequences
    SELECT 
        r.id,
        r.secuencia,
        r.bastidor,
        r.modelo,
        r.fecha_montaje,
        r.rn AS seq_idx
    FROM (
        SELECT 
            j2.id,
            j2.secuencia,
            j2.bastidor,
            j2.modelo,
            j2.fecha_montaje,
            ROW_NUMBER() OVER (ORDER BY j2.id) AS rn
        FROM dbo.JAULA_ERP j2
        WHERE j2.id > @LastCompletedID
    ) r
    WHERE r.rn <= @N
),
Latest_Log AS (
    SELECT 
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
)
SELECT 
    t.seq_idx AS [Indice],
    t.secuencia AS [Secuencia],
    t.bastidor AS [Bastidor],
    t.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), TRY_CAST(t.fecha_montaje AS DATE), 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), p.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), p.[Fin Planificado], 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN l.FECHA_HORA_FIN_SEC IS NULL OR p.[Fin Planificado] IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM Today_Seqs t
LEFT JOIN Planned_With_Times p ON t.seq_idx = p.seq_idx
LEFT JOIN Latest_Log l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje AND l.rn = 1
ORDER BY t.seq_idx ASC;
"""

cursor.execute(query, test_date)
rows = cursor.fetchall()
print(f"Results count: {len(rows)}")
for r in rows:
    print(r)

cursor.close()
conn.close()
