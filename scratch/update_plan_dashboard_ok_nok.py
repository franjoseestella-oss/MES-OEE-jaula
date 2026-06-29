import json
import copy

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

# Load current dashboard JSON
with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Print existing panel IDs
existing_ids = [p.get("id") for p in db.get("panels", [])]
print(f"Existing panel IDs before: {existing_ids}")

# Filter out any panels that already have ID 9 or 11 (just in case they were created in some previous attempt)
db["panels"] = [p for p in db["panels"] if p.get("id") not in (9, 11)]

# Update time bounds
db["time"] = {
    "from": "now/d+7h",
    "to": "now/d+15h"
}

# Update grid positions and queries
for panel in db["panels"]:
    p_id = panel.get("id")
    if p_id == 1:
        # SECUENCIAS PLANIFICADAS
        panel["gridPos"] = {"h": 4, "w": 4, "x": 0, "y": 0}
    elif p_id == 2:
        # SECUENCIAS COMPLETADAS (REAL)
        panel["gridPos"] = {"h": 4, "w": 5, "x": 4, "y": 0}
        panel["fieldConfig"] = {
            "defaults": {
                "color": {
                    "fixedColor": "#00D3FF",
                    "mode": "fixed"
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
        }
        # Update query to only return Completed Total
        panel["targets"][0]["rawSql"] = (
            "DECLARE @ActiveDate VARCHAR(8);\n"
            "SET @ActiveDate = CONVERT(varchar(8), CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE), 112);\n\n"
            "DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);\n\n"
            "SELECT \n"
            "    COUNT(DISTINCT log.NBASTIDOR) AS [Total]\n"
            "FROM dbo.LOG_TABLA log\n"
            "INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR\n"
            "WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL\n"
            "  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;"
        )
    elif p_id == 3:
        # DESVIACION
        panel["gridPos"] = {"h": 4, "w": 5, "x": 19, "y": 0}

# Create Panel 9 (SECUENCIAS OK)
# Let's clone Panel 2 config to base it on
panel_2_ref = None
for panel in db["panels"]:
    if panel.get("id") == 2:
        panel_2_ref = panel
        break

if not panel_2_ref:
    raise ValueError("Panel 2 not found to copy from")

panel_9 = copy.deepcopy(panel_2_ref)
panel_9["id"] = 9
panel_9["title"] = "SECUENCIAS OK"
panel_9["gridPos"] = {"h": 4, "w": 5, "x": 9, "y": 0}
panel_9["fieldConfig"]["defaults"]["color"] = {
    "fixedColor": "#2FD06A",
    "mode": "fixed"
}
panel_9["targets"][0]["rawSql"] = (
    "DECLARE @ActiveDate VARCHAR(8);\n"
    "SET @ActiveDate = CONVERT(varchar(8), CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE), 112);\n\n"
    "DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);\n\n"
    "SELECT \n"
    "    COUNT(DISTINCT CASE WHEN log.OK_NOK = 'OK' THEN log.NBASTIDOR END) AS [OK]\n"
    "FROM dbo.LOG_TABLA log\n"
    "INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR\n"
    "WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL\n"
    "  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;"
)

# Create Panel 11 (SECUENCIAS NOK)
panel_11 = copy.deepcopy(panel_2_ref)
panel_11["id"] = 11
panel_11["title"] = "SECUENCIAS NOK"
panel_11["gridPos"] = {"h": 4, "w": 5, "x": 14, "y": 0}
panel_11["fieldConfig"]["defaults"]["color"] = {
    "fixedColor": "#E32636",
    "mode": "fixed"
}
panel_11["targets"][0]["rawSql"] = (
    "DECLARE @ActiveDate VARCHAR(8);\n"
    "SET @ActiveDate = CONVERT(varchar(8), CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE), 112);\n\n"
    "DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);\n\n"
    "SELECT \n"
    "    COUNT(DISTINCT CASE WHEN log.OK_NOK = 'NOK' THEN log.NBASTIDOR END) AS [NOK]\n"
    "FROM dbo.LOG_TABLA log\n"
    "INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR\n"
    "WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL\n"
    "  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;"
)

# Insert the new panels back into the panels list. We can insert them right after panel 2.
new_panels = []
for p in db["panels"]:
    new_panels.append(p)
    if p.get("id") == 2:
        new_panels.append(panel_9)
        new_panels.append(panel_11)

db["panels"] = new_panels

existing_ids_after = [p.get("id") for p in db.get("panels", [])]
print(f"Existing panel IDs after: {existing_ids_after}")

# Write back
with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Local plan_dashboard.json successfully updated.")
