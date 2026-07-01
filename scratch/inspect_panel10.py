import json

path = r"grafana/provisioning/dashboards/plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 Title:", p.get("title"))
        print("Panel 10 Type:", p.get("type"))
        # Print color mapping / value mappings
        print("Field Config Mappings:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("mappings", []), indent=2))
        print("Thresholds:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("thresholds", []), indent=2))
        print("Custom Config:")
        print(json.dumps(p.get("options", {}), indent=2))
