import json
import os

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Preamble fallback date check
preamble = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 CONVERT(varchar(8), FECHA_MONTAJE, 112) FROM LOG_TABLA WHERE TRY_CAST(FECHA_HORA_INICIO_SEC AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

DECLARE @DashboardDate DATE = TRY_CAST(@ActiveDate AS DATE);
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

DECLARE @UnidadesAFabricar DECIMAL(4,1);
SELECT @UnidadesAFabricar = COALESCE(Cant_A_Fabricar, 18.0)
FROM dbo.CALENDARIO_LABORAL
WHERE Fecha = @DashboardDate;

IF @UnidadesAFabricar IS NULL
    SET @UnidadesAFabricar = 18.0;

DECLARE @N INT = CEILING(@UnidadesAFabricar);

DECLARE @Count185 INT = 0;
SELECT @Count185 = COUNT(*)
FROM dbo.CALENDARIO_LABORAL
WHERE Laborable = 1 
  AND Cant_A_Fabricar = 18.5 
  AND Fecha <= @DashboardDate;

DECLARE @UseSecondSet185 BIT = 0;
IF @Count185 > 0 AND @Count185 % 2 = 0
    SET @UseSecondSet185 = 1;

DECLARE @LastCompletedID INT;
SELECT TOP 1 @LastCompletedID = erp.id
FROM dbo.JAULA_ERP erp
INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
WHERE TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2) < @ShiftStart
  AND log.OK_NOK = 'OK'
ORDER BY erp.id DESC;

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP
    WHERE fecha_montaje = @ActiveDate;
END

IF @LastCompletedID IS NULL
BEGIN
    SELECT @LastCompletedID = MIN(id) - 1
    FROM dbo.JAULA_ERP;
END;

IF OBJECT_ID('tempdb..#ShiftSchedule') IS NOT NULL
    DROP TABLE #ShiftSchedule;

CREATE TABLE #ShiftSchedule (
    seq_idx INT,
    horario TIME
);

IF @UnidadesAFabricar = 18.0
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END
ELSE IF @UnidadesAFabricar = 19.0
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_19;
END
ELSE IF @UnidadesAFabricar = 18.5
BEGIN
    IF @UseSecondSet185 = 1
    BEGIN
        INSERT INTO #ShiftSchedule (seq_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 20 AND 38;
    END
    ELSE
    BEGIN
        INSERT INTO #ShiftSchedule (seq_idx, horario)
        SELECT ROW_NUMBER() OVER (ORDER BY id), horario
        FROM dbo.HHSS_18_5
        WHERE id BETWEEN 1 AND 19;
    END
END
ELSE
BEGIN
    INSERT INTO #ShiftSchedule (seq_idx, horario)
    SELECT ROW_NUMBER() OVER (ORDER BY id), horario
    FROM dbo.HHSS_18;
END;
"""

# Queries for each panel
query_panel1 = preamble + """
WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
)
SELECT COALESCE(MAX(seq_idx), 0) AS [Teórico]
FROM Planned_With_Times
WHERE [Fin Planificado] <= @EvalTime;
"""

query_panel2 = preamble + """
WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
)
SELECT COUNT(*) AS [Real]
FROM Today_Seqs t
INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
  AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
  AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
  AND l.OK_NOK = 'OK';
"""

query_panel3 = preamble + """
WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
),
Teorico_Count AS (
    SELECT COALESCE(MAX(seq_idx), 0) AS teorico
    FROM Planned_With_Times
    WHERE [Fin Planificado] <= @EvalTime
),
Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
),
Real_Count AS (
    SELECT COUNT(*) AS real
    FROM Today_Seqs t
    INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
    WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
      AND l.OK_NOK = 'OK'
)
SELECT 
    r.real - t.teorico AS [Desviación]
FROM Real_Count r, Teorico_Count t;
"""

query_panel4_a = preamble + """
WITH Planned_With_Times AS (
    SELECT 
        s.seq_idx,
        CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM #ShiftSchedule s
)
SELECT time, [Teórico] FROM (
    SELECT 
        @ShiftStart AS time,
        0 AS [Teórico]
    UNION ALL
    SELECT 
        [Fin Planificado] AS time,
        seq_idx AS [Teórico]
    FROM Planned_With_Times
    WHERE [Fin Planificado] <= DATEADD(hour, 15, CAST(@DashboardDate AS DATETIME))
) t
ORDER BY time;
"""

query_panel4_b = preamble + """
WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
)
SELECT time, [Real] FROM (
    SELECT 
        @ShiftStart AS time,
        0 AS [Real]
    UNION ALL
    SELECT 
        TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) AS time,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2)) AS [Real]
    FROM Today_Seqs t
    INNER JOIN dbo.LOG_TABLA l ON t.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = t.fecha_montaje
    WHERE t.seq_idx >= 1 AND t.seq_idx <= @N
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart
      AND TRY_CAST(l.FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime
      AND l.OK_NOK = 'OK'
) t
ORDER BY time;
"""

query_panel5 = preamble + """
WITH Today_Seqs AS (
    SELECT 
        j2.id,
        j2.secuencia,
        j2.bastidor,
        j2.modelo,
        j2.fecha_montaje,
        ROW_NUMBER() OVER (ORDER BY j2.id) AS seq_idx
    FROM dbo.JAULA_ERP j2
    WHERE j2.id > @LastCompletedID
),
Planned_Times AS (
    SELECT
        t.id,
        t.secuencia,
        t.bastidor,
        t.modelo,
        t.fecha_montaje,
        t.seq_idx,
        CASE 
            WHEN t.seq_idx = 1 THEN @ShiftStart
            ELSE CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s_prev.horario, 108)) AS DATETIME)
        END AS [Inicio Planificado],
        CAST(CONCAT(CONVERT(VARCHAR(10), @DashboardDate, 120), ' ', CONVERT(VARCHAR(8), s_curr.horario, 108)) AS DATETIME) AS [Fin Planificado]
    FROM Today_Seqs t
    INNER JOIN #ShiftSchedule s_curr ON t.seq_idx = s_curr.seq_idx
    LEFT JOIN #ShiftSchedule s_prev ON (t.seq_idx - 1) = s_prev.seq_idx
    WHERE t.seq_idx <= @N
),
Row0 AS (
    SELECT TOP 1
        erp.id,
        erp.secuencia,
        erp.bastidor,
        erp.modelo,
        erp.fecha_montaje,
        0 AS seq_idx,
        CAST(NULL AS DATETIME) AS [Inicio Planificado],
        CAST(NULL AS DATETIME) AS [Fin Planificado]
    FROM dbo.JAULA_ERP erp
    INNER JOIN dbo.LOG_TABLA log ON log.NSECUENCIA = erp.secuencia AND log.FECHA_MONTAJE = erp.fecha_montaje
    WHERE erp.id = @LastCompletedID
),
Combined_List AS (
    SELECT * FROM Row0
    UNION ALL
    SELECT * FROM Planned_Times
),
Latest_Log AS (
    SELECT 
        NBASTIDOR,
        FECHA_MONTAJE,
        OK_NOK,
        FECHA_HORA_INICIO_SEC,
        FECHA_HORA_FIN_SEC,
        ROW_NUMBER() OVER (PARTITION BY NBASTIDOR, FECHA_MONTAJE ORDER BY id DESC) as rn
    FROM dbo.LOG_TABLA
)
SELECT 
    c.secuencia AS [Secuencia],
    c.bastidor AS [Bastidor],
    c.modelo AS [Modelo],
    COALESCE(CONVERT(varchar(10), TRY_CAST(c.fecha_montaje AS DATE), 103), '') AS [Fecha Montaje],
    CONVERT(varchar(8), c.[Inicio Planificado], 108) AS [Inicio Planificado],
    CONVERT(varchar(8), c.[Fin Planificado], 108) AS [Fin Planificado],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_INICIO_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Inicio Real],
    CONVERT(varchar(8), CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time', 108) AS [Fin Real],
    CASE 
        WHEN c.seq_idx = 0 THEN '-'
        WHEN l.FECHA_HORA_FIN_SEC IS NULL THEN '-'
        ELSE 
            CASE 
                WHEN DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) > 0 
                    THEN '+' + CAST(DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
                ELSE 
                    CAST(DATEDIFF(minute, c.[Fin Planificado], CAST(CAST(l.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATETIME)) AS VARCHAR) + ' min'
            END
    END AS [Desviación],
    COALESCE(l.OK_NOK, 'Pendiente') AS [Estado]
FROM Combined_List c
LEFT JOIN Latest_Log l ON c.bastidor = l.NBASTIDOR AND l.FECHA_MONTAJE = c.fecha_montaje AND l.rn = 1
ORDER BY c.seq_idx ASC;
"""

query_panel8 = """SELECT
  fichero AS [Fichero Excel],
  regularizacion AS [Regularización],
  CONVERT(varchar(5), hora_inicio_jornada, 108) AS [Inicio Jornada],
  CONVERT(varchar(5), hora_inicio_parada, 108) AS [Inicio Parada],
  CONVERT(varchar(5), duracion_parada, 108) AS [Duración Parada],
  CONVERT(varchar(5), hora_fin_jornada, 108) AS [Fin Jornada]
FROM dbo.TURNO_TRABAJO"""

# Apply query changes
for p in db.get("panels", []):
    pid = p.get("id")
    if pid == 1:
        p["targets"][0]["rawSql"] = query_panel1
    elif pid == 2:
        p["targets"][0]["rawSql"] = query_panel2
    elif pid == 3:
        p["targets"][0]["rawSql"] = query_panel3
    elif pid == 4:
        for t in p["targets"]:
            if t.get("refId") == "A":
                t["rawSql"] = query_panel4_a
            elif t.get("refId") == "B":
                t["rawSql"] = query_panel4_b
    elif pid == 5:
        p["targets"][0]["rawSql"] = query_panel5

# Check if Panel 8 already exists, if so delete it so we start clean
db["panels"] = [p for p in db.get("panels", []) if p.get("id") != 8]

# Create Panel 8 structure
panel8 = {
  "datasource": {
    "uid": "mes_sqlserver"
  },
  "fieldConfig": {
    "defaults": {
      "custom": {
        "align": "auto",
        "cellOptions": {
          "type": "auto"
        },
        "inspect": False
      },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {
            "color": "green",
            "value": None
          }
        ]
      }
    },
    "overrides": []
  },
  "gridPos": {
    "h": 11,
    "w": 12,
    "x": 12,
    "y": 20
  },
  "id": 8,
  "options": {
    "cellHeight": "sm",
    "footer": {
      "countRows": False,
      "fields": "",
      "reducer": [
        "sum"
      ],
      "show": False
    },
    "showHeader": True,
    "sortBy": []
  },
  "pluginVersion": "10.4.2",
  "targets": [
    {
      "datasource": {
        "type": "mssql",
        "uid": "mes_sqlserver"
      },
      "editorMode": "code",
      "format": "table",
      "rawQuery": True,
      "rawSql": query_panel8,
      "refId": "A"
    }
  ],
  "title": "📅 DISTRIBUCIÓN DE LA JORNADA LABORAL (TURNO)",
  "type": "table"
}

db["panels"].append(panel8)

# Save back to file
with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Dashboard updated successfully!")
