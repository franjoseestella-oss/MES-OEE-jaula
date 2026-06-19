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

sql_query = """
SELECT TOP 10 
    erp.secuencia, 
    erp.bastidor, 
    erp.fecha_montaje AS erp_date, 
    log.FECHA_MONTAJE AS log_date,
    log.OK_NOK
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NBASTIDOR = erp.bastidor
WHERE TRY_CAST(erp.fecha_montaje AS DATE) <> log.FECHA_MONTAJE;
"""

try:
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    print("Different dates found:")
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)
conn.close()
