import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    print(f"ID: {p.get('id')}, Type: {p.get('type')}, Title: {p.get('title')}")
