import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

test_query = """
    DECLARE @PlotDate DATE = '2026-06-29';
    DECLARE @UTCOffset INT = 2;
    DECLARE @CurrentProgressTime DATETIME = '2026-06-29 09:30:00';

    SELECT TOP 10 
        FECHA_Y_HORA,
        DURACION,
        DATEADD(hour, -@UTCOffset, 
            CASE 
                WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN
                    TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103)
                ELSE
                    TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME)
            END
        ) AS alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN @CurrentProgressTime
            ELSE DATEADD(second, COALESCE(parts.hrs * 3600 + parts.mins * 60 + parts.secs, 0), 
                 DATEADD(hour, -@UTCOffset, 
                    CASE 
                        WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN
                            TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103)
                        ELSE
                            TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME)
                    END
                 ))
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
    ORDER BY id DESC
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(test_query)
    for row in cursor.fetchall():
        print(f"Raw: {row[0]} | Dur: {row[1]} | Start: {row[2]} | End: {row[3]}")
except Exception as e:
    print("Error:", e)
