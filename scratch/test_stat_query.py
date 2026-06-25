import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = """
    DECLARE @SelectedDate DATE = '2026-06-25';
    
    SELECT 
        COUNT(DISTINCT log.NBASTIDOR) AS [Total],
        SUM(CASE WHEN log.OK_NOK = 'OK' THEN 1 ELSE 0 END) AS [OK],
        SUM(CASE WHEN log.OK_NOK = 'NOK' THEN 1 ELSE 0 END) AS [NOK]
    FROM dbo.LOG_TABLA log
    INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
    WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
      AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;
    """
    cursor.execute(query)
    row = cursor.fetchone()
    print("Columns:", [col[0] for col in cursor.description])
    print("Values:", row)
    
except Exception as e:
    print("Error:", e)
