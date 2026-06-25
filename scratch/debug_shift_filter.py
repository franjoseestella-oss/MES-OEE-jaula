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
    DECLARE @DashboardDate DATE = '2026-06-25';
    
    SELECT 
        id,
        FECHA_HORA_FIN_SEC,
        CONVERT(varchar(50), CAST(CAST(FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS local_dt,
        CONVERT(varchar(50), DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME))) AS shift_start,
        CONVERT(varchar(50), DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME))) AS shift_end,
        CASE WHEN CAST(CAST(FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) >= DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME)) THEN 1 ELSE 0 END AS after_start,
        CASE WHEN CAST(CAST(FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME) <= DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME)) THEN 1 ELSE 0 END AS before_end
    FROM dbo.LOG_TABLA
    WHERE FECHA_HORA_FIN_SEC IS NOT NULL
      AND id >= 8339;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    for r in rows:
        print(f"id={r[0]}, raw={r[1]}")
        print(f"  local_dt={r[2]}")
        print(f"  shift_start={r[3]}")
        print(f"  shift_end={r[4]}")
        print(f"  is_after_start={r[5]}, is_before_end={r[6]}")
        
except Exception as e:
    print("Error:", e)
