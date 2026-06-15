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

query = """
DECLARE @ActiveDate VARCHAR(8) = '20260615';
DECLARE @ActiveDateDate DATE = CAST(@ActiveDate AS DATE);
DECLARE @ShiftStartActive DATETIME = DATEADD(hour, 7, CAST(@ActiveDateDate AS DATETIME));

WITH Start_Sec_ID AS (
    SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStartActive
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    ) AS Start_ERP_ID
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        -- Total active seconds: 455 minutes * 60 = 27300
        CASE 
            WHEN total_seqs > 0 THEN 27300.0 / total_seqs 
            ELSE 1516.66667 -- Default cycle time for 18 sequences (25.28 mins)
        END AS cycle_time
    FROM Total_Sec
),
Sec_Today AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        ROW_NUMBER() OVER (ORDER BY id) AS seq_idx,
        p.total_seqs,
        p.cycle_time
    FROM JAULA_ERP j
    CROSS JOIN Params p
    WHERE j.id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        id,
        secuencia,
        bastidor,
        modelo,
        seq_idx,
        -- Active start seconds = (seq_idx - 1) * cycle_time
        -- If start active seconds >= 180 min (10800 seconds), we add 25 min (1500 seconds) of break time
        DATEADD(second, 
            CAST((seq_idx - 1) * cycle_time AS INT) + 
            CASE WHEN (seq_idx - 1) * cycle_time >= 10800 THEN 1500 ELSE 0 END, 
            @ShiftStartActive
        ) AS [Inicio Planificado],
        -- Active end seconds = seq_idx * cycle_time
        -- If end active seconds > 180 min (10800 seconds), we add 25 min (1500 seconds) of break time
        DATEADD(second, 
            CAST(seq_idx * cycle_time AS INT) + 
            CASE WHEN seq_idx * cycle_time > 10800 THEN 1500 ELSE 0 END, 
            @ShiftStartActive
        ) AS [Fin Planificado]
    FROM Sec_Today
),
Latest_Log AS (
    SELECT 
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM LOG_TABLA
)
SELECT 
    j.secuencia AS [Secuencia],
    j.bastidor AS [Bastidor],
    j.modelo AS [Modelo],
    CONVERT(varchar(8), p.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), p.[Fin Planificado], 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado],
    p.seq_idx
FROM JAULA_ERP j
LEFT JOIN Planned_Times p ON j.id = p.id
LEFT JOIN Latest_Log l ON j.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = j.fecha_montaje AND l.rn = 1
WHERE j.fecha_montaje = @ActiveDate
ORDER BY j.id ASC
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    print("--- QUERY RESULTS ---")
    print(f"{'Seq':<5} | {'Bastidor':<14} | {'Modelo':<8} | {'Inicio Plan':<11} | {'Fin Plan':<11} | {'Inicio Real':<11} | {'Fin Real':<11} | {'Estado':<10} | {'Idx':<3}")
    print("-" * 120)
    for r in rows:
        print(f"{str(r[0]):<5} | {str(r[1]):<14} | {str(r[2]):<8} | {str(r[3]):<11} | {str(r[4]):<11} | {str(r[5]):<11} | {str(r[6]):<11} | {str(r[7]):<10} | {str(r[8]):<3}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
