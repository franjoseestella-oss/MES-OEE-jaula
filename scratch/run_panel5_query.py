import pyodbc

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

query = """
SET NOCOUNT ON;
DECLARE @ActiveDate VARCHAR(8) = '20260615';

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTime DATETIME = @ShiftEnd;

DECLARE @UnidadesAFabricar DECIMAL(4,1) = 18.0;
DECLARE @N INT = CEILING(@UnidadesAFabricar);

DECLARE @Count185 INT = 0;
DECLARE @UseSecondSet185 BIT = 0;

DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < @ShiftStart
  AND log.OK_NOK = 'OK'
ORDER BY erp.id DESC;

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP
    WHERE fecha_montaje = @ActiveDate;
END

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP;
END;

IF OBJECT_ID('tempdb..#ShiftSchedule') IS NOT NULL
    DROP TABLE #ShiftSchedule;

CREATE TABLE #ShiftSchedule (
    seq_idx INT,
    horario TIME
);

INSERT INTO #ShiftSchedule (seq_idx, horario)
SELECT ROW_NUMBER() OVER (ORDER BY id), horario
FROM dbo.HHSS_18;

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
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
)
SELECT 
    c.id,
    c.secuencia AS [Secuencia],
    c.bastidor AS [Bastidor],
    c.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), TRY_CAST(c.fecha_montaje AS DATE), 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), c.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), c.[Fin Planificado], 108) AS [Fin Planificado],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM Combined_List c
LEFT JOIN Latest_Log l ON c.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = c.fecha_montaje AND l.rn = 1
ORDER BY c.seq_idx ASC;
"""

cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    print(r)
