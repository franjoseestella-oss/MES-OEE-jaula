import json
with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            print(t.get("rawSql"))
