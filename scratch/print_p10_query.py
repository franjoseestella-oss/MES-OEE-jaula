import json

path = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print(p["targets"][0]["rawSql"])
