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
SELECT erp.id, erp.secuencia, erp.bastidor, log.fecha_creacion, log.OK_NOK
FROM JAULA_ERP erp
LEFT JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE erp.fecha_montaje = @ActiveDate
ORDER BY erp.id
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
