import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 FieldConfig:")
        print(json.dumps(p.get("fieldConfig", {}), indent=2))
        break
