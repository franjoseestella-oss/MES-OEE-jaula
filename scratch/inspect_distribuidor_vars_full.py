import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for var in dashboard.get("templating", {}).get("list", []):
    if var.get("name") in ["min_pct", "max_pct"]:
        print(f"=== Variable: {var.get('name')} ===")
        print(json.dumps(var, indent=2))
