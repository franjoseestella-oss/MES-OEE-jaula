import json

path = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 Title:", p.get("title"))
        print("Panel 10 Type:", p.get("type"))
        print("FieldConfig defaults:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}), indent=2))
        print("Mappings:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("mappings", []), indent=2))
