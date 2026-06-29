import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 10:
        for target in panel.get("targets", []):
            if target.get("refId") == "A":
                print(target.get("rawSql"))
