import json
import os

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update the default time range to match 07:00 - 15:00
data["time"] = {
    "from": "now/d+7h",
    "to": "now/d+15h"
}

# Define queries with correct 7-15 shift, lunch break, and dynamic pacing interval (450 minutes active time)
sql_panel_1 = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @DashboardDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @DashboardDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Start_Sec_ID AS (
    SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStart
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    ) AS Start_ERP_ID
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        CASE 
            WHEN total_seqs > 0 THEN 27300.0 / total_seqs 
            ELSE 1516.66667
        END AS cycle_time
    FROM Total_Sec
),
Sec_Today AS (
    SELECT 
        j.id,
        ROW_NUMBER() OVER (ORDER BY j.id) AS seq_idx,
        p.cycle_time
    FROM JAULA_ERP j
    CROSS JOIN Params p
    WHERE j.id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        seq_idx,
        DATEADD(second, 
            CAST(seq_idx * cycle_time AS INT) + 
            CASE WHEN seq_idx * cycle_time > 10800 THEN 1500 ELSE 0 END, 
            @ShiftStart
        ) AS [Fin Planificado]
    FROM Sec_Today
)
SELECT COALESCE(MAX(seq_idx), 0) AS [Teórico]
FROM Planned_Times
WHERE [Fin Planificado] <= @EvalTime"""

sql_panel_2 = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @DashboardDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @DashboardDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

SELECT COUNT(*) AS [Real]
FROM LOG_TABLA
WHERE fecha_creacion >= @ShiftStart
  AND fecha_creacion <= @EvalTime
  AND OK_NOK = 'OK'
  AND FECHA_MONTAJE = @ActiveDate"""

sql_panel_3 = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStart DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEnd DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTime DATETIME;

IF @DashboardDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTime = DATEADD(second, @TimeOfDayDiff, @ShiftStart);
END
ELSE IF @DashboardDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTime = @ShiftStart;
END
ELSE
BEGIN
    SET @EvalTime = @ShiftEnd;
END;

WITH Start_Sec_ID AS (
    SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStart
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    ) AS Start_ERP_ID
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        CASE 
            WHEN total_seqs > 0 THEN 27300.0 / total_seqs 
            ELSE 1516.66667
        END AS cycle_time
    FROM Total_Sec
),
Sec_Today AS (
    SELECT 
        j.id,
        ROW_NUMBER() OVER (ORDER BY j.id) AS seq_idx,
        p.cycle_time
    FROM JAULA_ERP j
    CROSS JOIN Params p
    WHERE j.id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        seq_idx,
        DATEADD(second, 
            CAST(seq_idx * cycle_time AS INT) + 
            CASE WHEN seq_idx * cycle_time > 10800 THEN 1500 ELSE 0 END, 
            @ShiftStart
        ) AS [Fin Planificado]
    FROM Sec_Today
),
Teorico_Count AS (
    SELECT COALESCE(MAX(seq_idx), 0) AS teorico
    FROM Planned_Times
    WHERE [Fin Planificado] <= @EvalTime
),
Real_Count AS (
    SELECT COUNT(*) AS real
    FROM LOG_TABLA
    WHERE fecha_creacion >= @ShiftStart
      AND fecha_creacion <= @EvalTime
      AND OK_NOK = 'OK'
      AND FECHA_MONTAJE = @ActiveDate
)
SELECT 
    r.real - t.teorico AS [Desviación]
FROM Real_Count r, Teorico_Count t"""

sql_panel_4_a = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStartActive DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));

WITH Start_Sec_ID AS (
    SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStartActive
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    ) AS Start_ERP_ID
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        CASE 
            WHEN total_seqs > 0 THEN 27300.0 / total_seqs 
            ELSE 1516.66667
        END AS cycle_time
    FROM Total_Sec
),
Sec_Today AS (
    SELECT 
        j.id,
        ROW_NUMBER() OVER (ORDER BY j.id) AS seq_idx,
        p.cycle_time
    FROM JAULA_ERP j
    CROSS JOIN Params p
    WHERE j.id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        seq_idx,
        DATEADD(second, 
            CAST(seq_idx * cycle_time AS INT) + 
            CASE WHEN seq_idx * cycle_time > 10800 THEN 1500 ELSE 0 END, 
            @ShiftStartActive
        ) AS [Fin Planificado]
    FROM Sec_Today
)
SELECT time, [Teórico] FROM (
    SELECT 
        DATEADD(hour, 7, CAST(CAST($__timeFrom() AS DATE) AS DATETIME)) AS time,
        0 AS [Teórico]
    UNION ALL
    SELECT 
        [Fin Planificado] AS time,
        seq_idx AS [Teórico]
    FROM Planned_Times
    WHERE [Fin Planificado] <= DATEADD(hour, 15, CAST(CAST($__timeFrom() AS DATE) AS DATETIME))
) t
ORDER BY time"""

sql_panel_4_b = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStartActive DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));
DECLARE @ShiftEndActive DATETIME = DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME));
DECLARE @EvalTimeActive DATETIME;

IF @DashboardDate = CAST(GETDATE() AS DATE)
BEGIN
    DECLARE @TimeOfDayDiff INT = DATEDIFF(second, DATEADD(hour, 7, CAST(CAST(GETDATE() AS DATE) AS DATETIME)), GETDATE());
    IF @TimeOfDayDiff < 0 SET @TimeOfDayDiff = 0;
    IF @TimeOfDayDiff > 28800 SET @TimeOfDayDiff = 28800;
    SET @EvalTimeActive = DATEADD(second, @TimeOfDayDiff, @ShiftStartActive);
END
ELSE IF @DashboardDate > CAST(GETDATE() AS DATE)
BEGIN
    SET @EvalTimeActive = @ShiftStartActive;
END
ELSE
BEGIN
    SET @EvalTimeActive = @ShiftEndActive;
END;

SELECT time, [Real] FROM (
    SELECT 
        DATEADD(hour, 7, CAST(CAST($__timeFrom() AS DATE) AS DATETIME)) AS time,
        0 AS [Real]
    UNION ALL
    SELECT 
        fecha_creacion AS time,
        ROW_NUMBER() OVER (ORDER BY fecha_creacion) AS [Real]
    FROM LOG_TABLA
    WHERE fecha_creacion >= @ShiftStartActive
      AND fecha_creacion <= @EvalTimeActive
      AND OK_NOK = 'OK'
      AND FECHA_MONTAJE = @ActiveDate
) t
ORDER BY time"""

sql_panel_5 = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = CAST($__timeFrom() AS DATE);
DECLARE @ShiftStartActive DATETIME = DATEADD(hour, 7, CAST(@DashboardDate AS DATETIME));

WITH Start_Sec_ID AS (
    SELECT COALESCE(
        (SELECT MAX(erp.id) + 1
         FROM JAULA_ERP erp
         INNER JOIN LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
         WHERE log.fecha_creacion < @ShiftStartActive
           AND log.OK_NOK = 'OK'
           AND erp.fecha_montaje = @ActiveDate),
        (SELECT MIN(id) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    ) AS Start_ERP_ID
),
Total_Sec AS (
    SELECT COUNT(*) AS total_seqs
    FROM JAULA_ERP
    WHERE id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND fecha_montaje = @ActiveDate
),
Params AS (
    SELECT 
        total_seqs,
        CASE 
            WHEN total_seqs > 0 THEN 27300.0 / total_seqs 
            ELSE 1516.66667
        END AS cycle_time
    FROM Total_Sec
),
Sec_Today AS (
    SELECT 
        id,
        secuencia,
        bastidor,
        modelo,
        ROW_NUMBER() OVER (ORDER BY id) AS seq_idx,
        p.cycle_time
    FROM JAULA_ERP j
    CROSS JOIN Params p
    WHERE j.id >= (SELECT Start_ERP_ID FROM Start_Sec_ID)
      AND j.fecha_montaje = @ActiveDate
),
Planned_Times AS (
    SELECT
        id,
        secuencia,
        bastidor,
        modelo,
        seq_idx,
        DATEADD(second, 
            CAST((seq_idx - 1) * cycle_time AS INT) + 
            CASE WHEN (seq_idx - 1) * cycle_time >= 10800 THEN 1500 ELSE 0 END, 
            @ShiftStartActive
        ) AS [Inicio Planificado],
        DATEADD(second, 
            CAST(seq_idx * cycle_time AS INT) + 
            CASE WHEN seq_idx * cycle_time > 10800 THEN 1500 ELSE 0 END, 
            @ShiftStartActive
        ) AS [Fin Planificado]
    FROM Sec_Today
),
Latest_Log AS (
    SELECT 
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM LOG_TABLA
)
SELECT 
    j.secuencia AS [Secuencia],
    j.bastidor AS [Bastidor],
    j.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), TRY_CAST(j.fecha_montaje AS DATE), 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), p.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), p.[Fin Planificado], 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN l.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, p.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM JAULA_ERP j
LEFT JOIN Planned_Times p ON j.id = p.id
LEFT JOIN Latest_Log l ON j.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = j.fecha_montaje AND l.rn = 1
WHERE j.fecha_montaje = @ActiveDate
ORDER BY j.id ASC"""

html_panel_6 = """<div style="display: flex; gap: 20px; align-items: stretch; justify-content: space-between; font-family: 'Inter', -apple-system, sans-serif; background: linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(168, 85, 247, 0.02) 100%); border: 1px solid rgba(168, 85, 247, 0.25); padding: 20px; border-radius: 8px; color: #ffffff;">
  <div style="flex: 1;">
    <h3 style="color: #a855f7; font-size: 1.2rem; margin: 0 0 10px 0; font-weight: 600;">ℹ️ Lógica Pacing / Pacemaker de Planta</h3>
    <p style="color: #a2aab7; font-size: 0.9rem; margin: 0; line-height: 1.5;">
      Este panel compara la producción teórica frente a la real. La lógica teórica inicia cada día a las <strong>07:00 AM</strong> partiendo de la primera secuencia del día. El turno es de 07:00 a 15:00, con parada por almuerzo de 10:00 a 10:25. El avance teórico distribuye uniformemente las secuencias planificadas a lo largo de las 7 horas y 35 minutos de producción activa (455 minutos en total), deteniendo el ritmo teórico durante el descanso.
    </p>
  </div>
  <div style="display: flex; align-items: center; justify-content: center; padding-left: 20px; border-left: 1px solid rgba(168, 85, 247, 0.15);">
    <a href="/d/panel-oee-mes-fabrica" style="display: inline-block; background: #a855f7; color: #ffffff; text-decoration: none; padding: 12px 24px; font-weight: 600; border-radius: 6px; font-size: 0.9rem; transition: all 0.2s ease; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);"
       onmouseover="this.style.background='#b566ff'; this.style.boxShadow='0 6px 16px rgba(168, 85, 247, 0.45)';"
       onmouseout="this.style.background='#a855f7'; this.style.boxShadow='0 4px 12px rgba(168, 85, 247, 0.3)';">
      Volver al Inicio
    </a>
  </div>
</div>"""

for panel in data["panels"]:
    p_id = panel.get("id")
    if p_id == 1:
        panel["targets"][0]["rawSql"] = sql_panel_1
    elif p_id == 2:
        panel["targets"][0]["rawSql"] = sql_panel_2
    elif p_id == 3:
        panel["targets"][0]["rawSql"] = sql_panel_3
    elif p_id == 4:
        panel["targets"][0]["rawSql"] = sql_panel_4_a
        panel["targets"][1]["rawSql"] = sql_panel_4_b
    elif p_id == 5:
        panel["targets"][0]["rawSql"] = sql_panel_5
    elif p_id == 6:
        panel["options"]["content"] = html_panel_6

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Dashboard JSON updated successfully.")
