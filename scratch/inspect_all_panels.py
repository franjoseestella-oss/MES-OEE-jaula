import json

file_path = "grafana/provisioning/dashboards/oee_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    print(f"ID: {panel.get('id')} | Title: '{panel.get('title')}' | Type: {panel.get('type')}")
