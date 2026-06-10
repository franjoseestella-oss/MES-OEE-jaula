import json
import copy

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Find Panel 9
panel_9_idx = -1
for i, p in enumerate(db.get("panels", [])):
    if p.get("id") == 9:
        panel_9_idx = i
        break

if panel_9_idx == -1:
    raise ValueError("Panel 9 not found in dashboard")

panel_9 = db["panels"][panel_9_idx]

# 1. Update Panel 9 (left panel, OK results)
panel_9["title"] = "REGISTRO DETALLADO DE PRUEBAS OK"
panel_9["gridPos"] = {"h": 10, "w": 12, "x": 0, "y": 25}

sql_9 = panel_9["targets"][0]["rawSql"]
# Insert the "AND OK_NOK = 'OK'" condition
if "AND OK_NOK =" not in sql_9:
    sql_9_updated = sql_9.replace(
        "WHERE fecha_creacion >= $__timeFrom() AND fecha_creacion <= $__timeTo()",
        "WHERE fecha_creacion >= $__timeFrom() AND fecha_creacion <= $__timeTo() AND OK_NOK = 'OK'"
    )
    panel_9["targets"][0]["rawSql"] = sql_9_updated

# 2. Duplicate to create Panel 16 (right panel, NOK results)
panel_16 = copy.deepcopy(panel_9)
panel_16["id"] = 16
panel_16["title"] = "REGISTRO DETALLADO DE PRUEBAS NOK"
panel_16["gridPos"] = {"h": 10, "w": 12, "x": 12, "y": 25}

sql_16 = panel_16["targets"][0]["rawSql"]
# Replace 'OK' with 'NOK'
sql_16_updated = sql_16.replace("AND OK_NOK = 'OK'", "AND OK_NOK = 'NOK'")
panel_16["targets"][0]["rawSql"] = sql_16_updated

# Insert Panel 16 after Panel 9
db["panels"].insert(panel_9_idx + 1, panel_16)

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully split Panel 9 into Panel 9 (OK) and Panel 16 (NOK) in log_dashboard.json!")
