import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for panel in dashboard.get("panels", []):
    title = panel.get('title')
    title_escaped = title.encode('ascii', 'backslashreplace').decode('ascii') if title else "None"
    print(f"Panel ID: {panel.get('id')}, Title: {title_escaped}, Type: {panel.get('type')}")
