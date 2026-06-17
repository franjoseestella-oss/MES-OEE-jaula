import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for panel in dashboard.get("panels", []):
    if panel.get("id") == 102:
        print("=== Panel 102: Mappings and Transformations ===")
        print("Transformations:")
        print(json.dumps(panel.get("transformations", []), indent=2))
        print("\nFieldConfig:")
        print(json.dumps(panel.get("fieldConfig", {}), indent=2))
        print("\nOverrides:")
        print(json.dumps(panel.get("fieldConfig", {}).get("overrides", []), indent=2))
