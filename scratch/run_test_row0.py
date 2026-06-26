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

test_date = '2026-06-24'

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

DECLARE @DashboardDate DATE = @ActiveDate;
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));

WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.modelo,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
),
Planned_Times AS (
    SELECT
        t.id,
        t.secuencia,
        t.bastidor,
        t.modelo,
        t.fecha_montaje,
        t.seq_idx,
        CASE 
            WHEN t.seq_idx = 1 THEN @ShiftStart
            ELSE CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s_prev.horario, 108)) AS DATETIME)
        END AS [Inicio Planificado],
        CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s_curr.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM Today_Seqs t
    INNER JOIN #ShiftSchedule s_curr ON t.seq_idx = s_curr.seq_idx
    LEFT JOIN #ShiftSchedule s_prev ON (t.seq_idx - 1) = s_prev.seq_idx
    WHERE t.seq_idx <= @N
),
Row0 AS (
    SELECT TOP 1
        erp.id,
        erp.secuencia,
        erp.bastidor,
        erp.modelo,
        erp.fecha_montaje,
        0 AS seq_idx,
        CAST(NULL AS DATETIME) AS [Inicio Planificado],
        CAST(NULL AS DATETIME) AS [Fin Planificado]
    FROM dbo.JAULA_ERP erp
    INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
    WHERE erp.id = @LastCompletedID
),
Combined_List AS (
    SELECT * FROM Row0
    UNION ALL
    SELECT * FROM Planned_Times
),
Latest_Log AS (
    SELECT 
        NBASTIDOR,
        NSECUENCIA,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NSECUENCIA ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
)
SELECT 
    c.secuencia AS [Secuencia],
    c.bastidor AS [Bastidor],
    c.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), TRY_CAST(c.fecha_montaje AS DATE), 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), c.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), c.[Fin Planificado], 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN c.seq_idx = 0 THEN '-'
        WHEN l.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                END
    END AS [Desviación],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM Combined_List c
LEFT JOIN Latest_Log l ON l.NSECUENCIA = TRY_CAST(c.secuencia AS INT) AND l.rn = 1
ORDER BY c.seq_idx ASC;
"""

cursor.execute(query, test_date)
rows = cursor.fetchall()
colnames = [desc[0] for desc in cursor.description]
print("\t".join(colnames))
for r in rows:
    print("\t".join(str(val) for val in r))

cursor.close()
conn.close()
