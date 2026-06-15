import json

file_path = "grafana/provisioning/dashboards/oee_dashboard.json"
with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") in (14, 17):
        print(f"--- Panel {p.get('id')} ({p.get('title')}) ---")
        # Print fieldConfig, options, and transformations
        print("FieldConfig defaults:")
        print(json.dumps(p.get("fieldConfig", {}).get("defaults", {}), indent=2))
        print("Options:")
        print(json.dumps(p.get("options", {}), indent=2))
        print("Transformations:")
        print(json.dumps(p.get("transformations", []), indent=2))
