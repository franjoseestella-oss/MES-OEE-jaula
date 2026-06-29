import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get mapped sequences for 2026-06-26
query = """
DECLARE @ActiveDate DATE = '2026-06-26';
DECLARE @UTCOffset INT = 2;

-- We will fetch the actual logs for these sequences from LOG_TABLA
SELECT 
    m.secuencia,
    m.bastidor,
    log.FECHA_HORA_INICIO_SEC,
    log.FECHA_HORA_FIN_SEC,
    log.OK_NOK
FROM (
    SELECT 
        secuencia,
        bastidor,
        modelo,
        TRY_CAST(fecha_montaje AS DATE) AS original_date,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
) m
LEFT JOIN (
    SELECT 
        NBASTIDOR,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        OK_NOK,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
) log ON log.NBASTIDOR = m.bastidor AND log.rn = 1
WHERE m.original_date = @ActiveDate
ORDER BY CAST(m.secuencia AS INT);
"""

cursor.execute(query)
for r in cursor.fetchall():
    print(f"Seq: {r[0]}, Bastidor: {r[1]}, Start: {r[2]}, End: {r[3]}, Status: {r[4]}")

conn.close()
