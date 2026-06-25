import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for i, p in enumerate(db.get("panels", [])):
    print(f"Index {i} | ID {p.get('id')} | Title: {p.get('title')} | Type: {p.get('type')} | gridPos: {p.get('gridPos')}")
