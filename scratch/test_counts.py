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
    
    # Simulate @ActiveDate = '2026-06-25'
    query = """
    DECLARE @SelectedDate DATE = '2026-06-25';
    
    SELECT COUNT(DISTINCT log.NBASTIDOR) AS [Real]
    FROM dbo.LOG_TABLA log
    INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
    WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
      AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;
    """
    cursor.execute(query)
    row = cursor.fetchone()
    print("Real count for 2026-06-25:", row[0])
    
except Exception as e:
    print("Error:", e)
