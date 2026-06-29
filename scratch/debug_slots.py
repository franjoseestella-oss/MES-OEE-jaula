import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get the CTE definition from test_out_of_order_query_v2.py
# Let's run a query that outputs the computed slots/sequences for 2026-06-29.
sql_debug = """
DECLARE @ShiftStart DATETIME = '2026-06-29 05:00:00';
DECLARE @ShiftEnd DATETIME = '2026-06-29 13:00:00';

WITH OrderedERP AS (
    SELECT 
        secuencia,
        bastidor,
        modelo,
        ROW_NUMBER() OVER (ORDER BY secuencia) as idx
    FROM dbo.JAULA_ERP
    WHERE CONVERT(DATE, fecha_insert) = CONVERT(DATE, @ShiftStart)
),
ERPWithTimes AS (
    SELECT 
        idx,
        secuencia,
        bastidor,
        modelo,
        DATEADD(SECOND, (idx - 1) * 330, @ShiftStart) as planned_start,
        DATEADD(SECOND, idx * 330, @ShiftStart) as planned_end
    FROM OrderedERP
),
SequenceTimes AS (
    SELECT 
        e.idx as slot_idx,
        e.secuencia,
        e.bastidor,
        e.modelo,
        e.planned_start,
        e.planned_end,
        -- Actual start
        CASE 
            WHEN e.idx = 1 THEN @ShiftStart
            ELSE COALESCE(
                (SELECT MIN(CAST(FECHA AS DATETIME)) FROM dbo.LOG_TABLA l WHERE l.NBASTIDOR = e.bastidor),
                CASE 
                    WHEN e.bastidor = (SELECT NBASTIDOR FROM dbo.REFERENCIA_EN_CICLO) 
                    THEN (
                        SELECT TOP 1 CAST(CONCAT(
                            CONVERT(VARCHAR(10), @ShiftStart, 120), ' ', 
                            SUBSTRING(FECHA_INICIO_CICLO, 1, 5), ':00'
                        ) AS DATETIME)
                        FROM dbo.REFERENCIA_EN_CICLO
                    )
                    ELSE NULL 
                END
            )
        END as actual_start_local
    FROM ERPWithTimes e
)
SELECT 
    secuencia,
    bastidor,
    planned_start,
    planned_end,
    actual_start_local,
    -- Convert to UTC since the main query uses DATEADD(hour, -2, ...) or similar
    DATEADD(hour, -2, planned_start) as planned_start_utc,
    DATEADD(hour, -2, planned_end) as planned_end_utc,
    DATEADD(hour, -2, actual_start_local) as actual_start_utc
FROM SequenceTimes
WHERE secuencia = '0261';
"""

cursor.execute(sql_debug)
row = cursor.fetchone()
print(f"secuencia: {row[0]}")
print(f"bastidor: {row[1]}")
print(f"planned_start: {row[2]}")
print(f"planned_end: {row[3]}")
print(f"actual_start_local: {row[4]}")
print(f"planned_start_utc: {row[5]}")
print(f"planned_end_utc: {row[6]}")
print(f"actual_start_utc: {row[7]}")

conn.close()
