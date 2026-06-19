import json

for filepath in ["grafana/provisioning/dashboards/distribuidor_dashboard.json", "grafana/provisioning/dashboards/plan_dashboard.json"]:
    with open(filepath, "r", encoding="utf-8") as f:
        db = json.load(f)
    print(f"File: {filepath} | UID: {db.get('uid')} | Title: {db.get('title')}")
