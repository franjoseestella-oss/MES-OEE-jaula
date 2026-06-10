import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") in [14, 15]:
        print(f"Panel ID: {p['id']} | Title: {p.get('title')}")
        print("  thresholds in defaults:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}).get("thresholds", {}), indent=2))
        print("  overrides:")
        print(json.dumps(p.get("fieldConfig", {}).get("overrides", []), indent=2))
        print("  transformations:")
        for t in p.get("transformations", []):
            if t.get("id") == "configFromData":
                print(f"    configFromData options: {json.dumps(t.get('options', {}), indent=2)}")
