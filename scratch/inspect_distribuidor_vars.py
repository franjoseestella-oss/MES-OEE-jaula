import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

templating = dashboard.get("templating", {})
for var in templating.get("list", []):
    print(f"Variable: {var.get('name')}, Type: {var.get('type')}, Current: {var.get('current')}")
