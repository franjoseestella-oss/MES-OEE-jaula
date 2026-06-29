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
    
    cursor.execute("""
    DECLARE @UTCOffset INT = 2; -- Romance Standard Time offset typically
    DECLARE @PlotDate DATE = '2026-06-26';
    DECLARE @CurrentProgressTime DATETIME = '2026-06-26 16:00:00';
    
    SELECT 
        id,
        FECHA_Y_HORA,
        DURACION,
        DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END)) AS alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN @CurrentProgressTime
            ELSE DATEADD(second, COALESCE(parts.hrs * 3600 + parts.mins * 60 + parts.secs, 0), 
                 DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END)))
        END AS alarm_end
    FROM dbo.LOG_ALARMAS
    CROSS APPLY (
        SELECT REPLACE(DURACION, ' ', '') AS clean_dur
    ) cd
    CROSS APPLY (
        SELECT 
            CHARINDEX('h', cd.clean_dur) AS h_pos,
            CHARINDEX('m', cd.clean_dur) AS m_pos,
            CHARINDEX('s', cd.clean_dur) AS s_pos
    ) pos
    CROSS APPLY (
        SELECT 
            CASE WHEN pos.h_pos > 0 THEN TRY_CAST(SUBSTRING(cd.clean_dur, 1, pos.h_pos - 1) AS INT) ELSE 0 END AS hrs,
            CASE 
                WHEN pos.m_pos > 0 THEN 
                    TRY_CAST(SUBSTRING(cd.clean_dur, 
                        CASE WHEN pos.h_pos > 0 THEN pos.h_pos + 1 ELSE 1 END, 
                        pos.m_pos - CASE WHEN pos.h_pos > 0 THEN pos.h_pos + 1 ELSE 1 END
                    ) AS INT)
                ELSE 0 
            END AS mins,
            CASE 
                WHEN pos.s_pos > 0 THEN 
                    TRY_CAST(SUBSTRING(cd.clean_dur, 
                        CASE 
                            WHEN pos.m_pos > 0 THEN pos.m_pos + 1 
                            WHEN pos.h_pos > 0 THEN pos.h_pos + 1 
                            ELSE 1 
                        END, 
                        pos.s_pos - CASE 
                            WHEN pos.m_pos > 0 THEN pos.m_pos + 1 
                            WHEN pos.h_pos > 0 THEN pos.h_pos + 1 
                            ELSE 1 
                        END
                    ) AS INT)
                ELSE 0 
            END AS secs
    ) parts
    WHERE FECHA_Y_HORA LIKE '[0-9]%' OR FECHA_Y_HORA LIKE '[0-9][0-9]%'
    """)
    for row in cursor.fetchall():
        print(row)
        
    conn.close()
except Exception as e:
    print("Error:", e)
