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

WITH Start_Sec AS (
    SELECT COALESCE(MAX(erp.id), (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)) AS Last_ERP_ID
    FROM JAULA_ERP erp
    INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
    WHERE log.fecha_creacion < @ShiftStartActive
      AND log.OK_NOK = 'OK'
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Last_ERP_ID + 1 FROM Start_Sec)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        CASE 
            WHEN total_seqs > 0 THEN CAST(ROUND(CAST(total_seqs AS FLOAT) * 180.0 / 455.0, 0) AS INT)
            ELSE 7
        END AS seqs_before
    FROM Total_Sec
),
Params2 AS (
    SELECT 
        total_seqs,
        seqs_before,
        CASE WHEN total_seqs - seqs_before > 0 THEN total_seqs - seqs_before ELSE 11 END AS seqs_after
    FROM Params
),
Params3 AS (
    SELECT
        total_seqs,
        seqs_before,
        seqs_after,
        CASE WHEN seqs_before > 0 THEN 180.0 * 60.0 / seqs_before ELSE 1542.857 END AS cycle_time_1,
        CASE WHEN seqs_after > 0 THEN 275.0 * 60.0 / seqs_after ELSE 1500.0 END AS cycle_time_2
    FROM Params2
),
Sec_Today AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        ROW_NUMBER() OVER (ORDER BY id) AS seq_idx,
        p.seqs_before,
        p.cycle_time_1,
        p.cycle_time_2
    FROM JAULA_ERP j
    CROSS JOIN Params3 p
    WHERE j.id >= (SELECT Last_ERP_ID + 1 FROM Start_Sec)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        id,
        secuencia,
        bastidor,
        modelo,
        seq_idx,
        CASE 
            WHEN seq_idx <= seqs_before 
                THEN DATEADD(second, CAST((seq_idx - 1) * cycle_time_1 AS INT), @ShiftStartActive)
            ELSE 
                DATEADD(second, CAST((seq_idx - seqs_before - 1) * cycle_time_2 AS INT), DATEADD(minute, 25, DATEADD(hour, 3, @ShiftStartActive)))
        END AS [Inicio Planificado],
        CASE 
            WHEN seq_idx <= seqs_before 
                THEN DATEADD(second, CAST(seq_idx * cycle_time_1 AS INT), @ShiftStartActive)
            ELSE 
                DATEADD(second, CAST((seq_idx - seqs_before) * cycle_time_2 AS INT), DATEADD(minute, 25, DATEADD(hour, 3, @ShiftStartActive)))
        END AS [Fin Planificado]
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
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
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
    print(f"{'Seq':<5} | {'Bastidor':<14} | {'Modelo':<8} | {'Inicio Plan':<11} | {'Fin Plan':<11} | {'Inicio Real':<11} | {'Fin Real':<11} | {'Estado':<10}")
    print("-" * 100)
    for r in rows:
        print(f"{str(r[0]):<5} | {str(r[1]):<14} | {str(r[2]):<8} | {str(r[3]):<11} | {str(r[4]):<11} | {str(r[5]):<11} | {str(r[6]):<11} | {str(r[7]):<10}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
