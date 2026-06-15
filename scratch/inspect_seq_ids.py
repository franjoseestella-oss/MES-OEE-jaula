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

SELECT 
    (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate) AS Min_ERP_ID,
    (SELECT MAX(erp.id) + 1
     FROM JAULA_ERP erp
     INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
     WHERE log.fecha_creacion < @ShiftStartActive
       AND log.OK_NOK = 'OK'
       AND erp.fecha_montaje = @ActiveDate) AS Last_ERP_Before_Shift,
    (SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStartActive
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    )) AS Start_ERP_ID
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    print("Min_ERP_ID:", row[0])
    print("Last_ERP_Before_Shift:", row[1])
    print("Start_ERP_ID:", row[2])
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
