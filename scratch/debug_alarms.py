import pyodbc
import dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
dotenv.load_dotenv()

host = os.getenv("SQL_SERVER_HOST", "DESKTOP-PMRMSPT\\SQLEXPRESS")
database = os.getenv("SQL_SERVER_DATABASE", "DAFEED")
user = os.getenv("SQL_SERVER_USER", "usuario_readonly")
password = os.getenv("SQL_SERVER_PASSWORD", "Logisnext2026!")
driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")

conn_str = f"DRIVER={{{driver}}};SERVER={host};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # We want to run a query to inspect #SeqsToSchedule and AlarmIntervals
    sql_debug = """
    SET NOCOUNT ON;
    DECLARE @PlotDate DATE = '2026-06-26';
    DECLARE @ShiftStartHour INT = 7;
    DECLARE @ShiftEndHour INT = 15;
    DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
    DECLARE @ShiftStartDT DATETIME = DATEADD(hour, @ShiftStartHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
    DECLARE @ShiftEndDT DATETIME = DATEADD(hour, @ShiftEndHour - @UTCOffset, CAST(@PlotDate AS DATETIME));

    -- Temp AlarmIntervals
    SELECT 
        id,
        FECHA_Y_HORA,
        DURACION,
        CASE 
            -- Format: "29/6/2026, 6:28:46"
            WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN 
                DATEADD(hour, -@UTCOffset, 
                    TRY_CONVERT(DATETIME, 
                        SUBSTRING(FECHA_Y_HORA, 1, CHARINDEX(',', FECHA_Y_HORA)-1) + ' ' + 
                        LTRIM(RTRIM(SUBSTRING(FECHA_Y_HORA, CHARINDEX(',', FECHA_Y_HORA)+1, LEN(FECHA_Y_HORA)))), 
                        103
                    )
                )
            -- Format: "6:28:50" (time only)
            ELSE 
                DATEADD(hour, -@UTCOffset, 
                    TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME)
                )
        END AS alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN 
                -- Use the actual max date/time of the day or right now
                DATEADD(hour, -@UTCOffset, GETDATE())
            WHEN DURACION LIKE '%s' THEN 
                DATEADD(second, TRY_CAST(SUBSTRING(DURACION, 1, LEN(DURACION)-1) AS INT),
                    CASE 
                        WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN 
                            DATEADD(hour, -@UTCOffset, 
                                TRY_CONVERT(DATETIME, 
                                    SUBSTRING(FECHA_Y_HORA, 1, CHARINDEX(',', FECHA_Y_HORA)-1) + ' ' + 
                                    LTRIM(RTRIM(SUBSTRING(FECHA_Y_HORA, CHARINDEX(',', FECHA_Y_HORA)+1, LEN(FECHA_Y_HORA)))), 
                                    103
                                )
                            )
                        ELSE 
                            DATEADD(hour, -@UTCOffset, 
                                TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME)
                            )
                    END
                )
            WHEN DURACION LIKE '%min' THEN 
                DATEADD(minute, TRY_CAST(SUBSTRING(DURACION, 1, LEN(DURACION)-3) AS INT),
                    CASE 
                        WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN 
                            DATEADD(hour, -@UTCOffset, 
                                TRY_CONVERT(DATETIME, 
                                    SUBSTRING(FECHA_Y_HORA, 1, CHARINDEX(',', FECHA_Y_HORA)-1) + ' ' + 
                                    LTRIM(RTRIM(SUBSTRING(FECHA_Y_HORA, CHARINDEX(',', FECHA_Y_HORA)+1, LEN(FECHA_Y_HORA)))), 
                                    103
                                )
                            )
                        ELSE 
                            DATEADD(hour, -@UTCOffset, 
                                TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME)
                            )
                    END
                )
            ELSE NULL
        END AS alarm_end
    INTO #AlarmIntervals
    FROM dbo.LOG_ALARMAS
    WHERE FECHA_Y_HORA LIKE '[0-9]%' OR FECHA_Y_HORA LIKE '[0-9][0-9]%';

    SELECT id, FECHA_Y_HORA, DURACION, alarm_start, alarm_end 
    FROM #AlarmIntervals
    WHERE alarm_start <= @ShiftEndDT AND alarm_end >= @ShiftStartDT;
    """
    
    cursor.execute(sql_debug)
    rows = cursor.fetchall()
    print("--- Alarms in shift time range ---")
    for r in rows:
        print(r)
        
    conn.close()
except Exception as e:
    print("Error:", e)
