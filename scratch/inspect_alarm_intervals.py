import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

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
DECLARE @PlotDate DATE = '2026-06-29';
DECLARE @UTCOffset INT = DATEDIFF(hour, GETUTCDATE(), GETDATE());
DECLARE @ShiftStartHour INT = 7; -- default
DECLARE @ShiftEndHour INT = 15; -- default
DECLARE @ShiftStartDT DATETIME = DATEADD(hour, @ShiftStartHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @ShiftEndDT DATETIME = DATEADD(hour, @ShiftEndHour - @UTCOffset, CAST(@PlotDate AS DATETIME));
DECLARE @CurrentProgressTime DATETIME = GETUTCDATE();

WITH AlarmBase AS (
    SELECT 
        id,
        DESCRIPCION,
        DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END)) AS alarm_start,
        DURACION,
        LEAD(DATEADD(hour, -@UTCOffset, (CASE WHEN CHARINDEX(',', FECHA_Y_HORA) > 0 THEN TRY_CONVERT(DATETIME, REPLACE(FECHA_Y_HORA, ',', ''), 103) ELSE TRY_CAST(CONVERT(VARCHAR(10), @PlotDate, 120) + ' ' + FECHA_Y_HORA AS DATETIME) END))) 
            OVER (PARTITION BY DESCRIPCION ORDER BY id ASC) AS next_alarm_start
    FROM dbo.LOG_ALARMAS
    WHERE (FECHA_Y_HORA LIKE '[0-9]%' OR FECHA_Y_HORA LIKE '[0-9][0-9]%')
      AND DESCRIPCION LIKE '%ALARMA CRÍTICA%'
),
AlarmIntervals AS (
    SELECT 
        id,
        DESCRIPCION,
        alarm_start,
        CASE 
            WHEN DURACION = 'Activa' THEN COALESCE(next_alarm_start, @CurrentProgressTime)
            ELSE DATEADD(second, COALESCE(parts.hrs * 3600 + parts.mins * 60 + parts.secs, 0), alarm_start)
        END AS alarm_end
    FROM AlarmBase
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
)
SELECT id, DESCRIPCION, alarm_start, alarm_end FROM AlarmIntervals
ORDER BY alarm_start DESC;
"""

cursor.execute(query)
for r in cursor.fetchall():
    print(f"ID: {r[0]}, DESC: {r[1]}, Start: {r[2]}, End: {r[3]}")

conn.close()
