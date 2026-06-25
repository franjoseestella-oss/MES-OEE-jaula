import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 Mappings:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("mappings", []), indent=2))
        print("Panel 10 Thresholds:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("thresholds", []), indent=2))
