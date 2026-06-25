import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 4:
        print("Panel 4 Query:")
        print(panel.get("targets", [])[0].get("rawSql"))
