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

query = """
SELECT NBASTIDOR, FECHA_INICIO_CICLO FROM dbo.REFERENCIA_EN_CICLO;
"""
cursor.execute(query)
print("REFERENCIA_EN_CICLO:")
for r in cursor.fetchall():
    print(r)

query2 = """
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
SELECT NBASTIDOR, FECHA_INICIO_CICLO,
    DATEADD(hour, -@UTCOffset, TRY_CONVERT(DATETIME, 
        SUBSTRING(FECHA_INICIO_CICLO, 13, 4) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 10, 2) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 7, 2) + 'T' + 
        SUBSTRING(FECHA_INICIO_CICLO, 1, 5) + ':00'
    )) AS converted
FROM dbo.REFERENCIA_EN_CICLO;
"""
cursor.execute(query2)
print("CONVERTED:")
for r in cursor.fetchall():
    print(r)

conn.close()
