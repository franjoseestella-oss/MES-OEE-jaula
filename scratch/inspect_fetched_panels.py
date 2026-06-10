import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    print(f"ID: {p.get('id')}, Title: {p.get('title')}, Type: {p.get('type')}")
