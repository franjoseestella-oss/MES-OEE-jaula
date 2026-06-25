import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Update Panel 2
p2_query = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

SELECT 
    COUNT(DISTINCT log.NBASTIDOR) AS [Total],
    SUM(CASE WHEN log.OK_NOK = 'OK' THEN 1 ELSE 0 END) AS [OK],
    SUM(CASE WHEN log.OK_NOK = 'NOK' THEN 1 ELSE 0 END) AS [NOK]
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;"""

# Update Panel 3
p3_query = """DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
CREATE TABLE #CalendarSlots (
    global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE
);

WITH CalendarBase AS (
    SELECT 
        Fecha,
        Laborable,
        Cant_A_Fabricar,
        SUM(CASE WHEN Cant_A_Fabricar = 18.5 THEN 1 ELSE 0 END) OVER (ORDER BY Fecha ASC) AS Count185
    FROM dbo.CALENDARIO_LABORAL
    WHERE Fecha >= '2026-06-24'
)
INSERT INTO #CalendarSlots (fecha)
SELECT 
    cb.Fecha
FROM CalendarBase cb
CROSS APPLY (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18
    WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_19
    WHERE cb.Cant_A_Fabricar = 19.0
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 1 AND id BETWEEN 1 AND 19
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 0 AND id BETWEEN 20 AND 38
) s
WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
ORDER BY cb.Fecha ASC, s.seq_idx ASC;

IF OBJECT_ID('tempdb..#MappedSeqs') IS NOT NULL DROP TABLE #MappedSeqs;
CREATE TABLE #MappedSeqs (
    id INT PRIMARY KEY,
    planned_date DATE
);

WITH OrderedERP AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
INSERT INTO #MappedSeqs (id, planned_date)
SELECT 
    o.id,
    cs.fecha
FROM OrderedERP o
INNER JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

DECLARE @Teorico INT, @Real INT;

SELECT @Teorico = COUNT(*)
FROM #MappedSeqs
WHERE planned_date = @SelectedDate;

SELECT @Real = COUNT(DISTINCT log.NBASTIDOR)
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;

SELECT COALESCE(@Real, 0) - COALESCE(@Teorico, 0) AS [Desviación];"""

for panel in db.get("panels", []):
    pid = panel.get("id")
    if pid == 2:
        # Update rawSql query
        panel["targets"][0]["rawSql"] = p2_query
        # Add color overrides
        panel["fieldConfig"]["overrides"] = [
            {
                "matcher": { "id": "byName", "options": "OK" },
                "properties": [ { "id": "color", "value": { "fixedColor": "#2FD06A", "mode": "fixed" } } ]
            },
            {
                "matcher": { "id": "byName", "options": "NOK" },
                "properties": [ { "id": "color", "value": { "fixedColor": "#E32636", "mode": "fixed" } } ]
            },
            {
                "matcher": { "id": "byName", "options": "Total" },
                "properties": [ { "id": "color", "value": { "fixedColor": "#00D3FF", "mode": "fixed" } } ]
            }
        ]
        print("Updated Panel 2 query and overrides.")
    elif pid == 3:
        panel["targets"][0]["rawSql"] = p3_query
        print("Updated Panel 3 query.")

with open(db_path, "w", encoding="utf-8") as fw:
    json.dump(db, fw, indent=2, ensure_ascii=False)

# Push back to Grafana
if "id" in db:
    del db["id"]
    
payload = {
    "dashboard": db,
    "folderUid": "dfovv23tkq48wc",
    "overwrite": True
}
auth = ("fran.jose.estella@gmail.com", "admin123")
url = "http://localhost:3010/api/dashboards/db"
headers = {"Content-Type": "application/json"}

res = requests.post(url, json=payload, auth=auth, headers=headers)
print(f"Grafana API Push Status Code: {res.status_code}")
print(f"Response: {res.text}")
