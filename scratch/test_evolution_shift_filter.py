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
    DECLARE @ActiveDate VARCHAR(8) = '20260625';
    DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
    DECLARE @PlotDate DATE = '2026-06-25';
    DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
    DECLARE @ShiftStart DATETIME = DATEADD(hour, 7 - @UTCOffset, CAST(@PlotDate AS DATETIME));

    SELECT time, [Real] FROM (
        SELECT 
            @ShiftStart AS time,
            0 AS [Real]
        UNION ALL
        SELECT 
            TRY_CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2) AS time,
            ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_FIN_SEC AS DATETIME2)) AS [Real]
        FROM dbo.LOG_TABLA l
        WHERE l.FECHA_HORA_FIN_SEC IS NOT NULL
          AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @DashboardDate
          AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) >= DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME))
          AND CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) <= DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME))
    ) t
    ORDER BY time;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print("Evolution query results with local shift filters:")
    for r in rows:
        print(f"time={r[0]}, Real={r[1]}")
        
except Exception as e:
    print("Error:", e)
