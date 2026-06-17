import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for panel in dashboard.get("panels", []):
    if panel.get("id") == 102:
        print("=== Panel 102 Target SQL Queries ===")
        for target in panel.get("targets", []):
            print(f"RefId: {target.get('refId')}")
            print(target.get("rawSql"))
