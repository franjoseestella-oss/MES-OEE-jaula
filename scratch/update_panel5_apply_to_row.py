import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

updated = False
for panel in db.get("panels", []):
    if panel.get("id") == 5:
        overrides = panel.get("fieldConfig", {}).get("overrides", [])
        for o in overrides:
            if o.get("matcher", {}).get("options") == "Estado":
                for prop in o.get("properties", []):
                    if prop.get("id") == "custom.cellOptions":
                        prop["value"] = {
                            "type": "color-background",
                            "applyToRow": True
                        }
                        updated = True
                        print("Updated custom.cellOptions to include applyToRow: True")
                        break

if not updated:
    print("Error: Could not find Panel 5 override for Estado.")
else:
    with open(db_path, "w", encoding="utf-8") as fw:
        json.dump(db, fw, indent=2, ensure_ascii=False)
    print("Successfully wrote updated plan_dashboard.json.")
