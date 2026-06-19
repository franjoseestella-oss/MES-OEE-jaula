import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

print(f"Dashboard Title: {db.get('title')}")
print(f"Dashboard UID: {db.get('uid')}")
print("Panels:")
for p in db.get("panels", []):
    print(f"ID: {p.get('id')} | Title: {p.get('title')} | Type: {p.get('type')} | GridPos: {p.get('gridPos')}")
