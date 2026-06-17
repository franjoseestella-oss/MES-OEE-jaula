import json

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

updated = False
for var in dashboard.get("templating", {}).get("list", []):
    if var.get("name") == "min_pct":
        print("Updating min_pct to 40...")
        var["query"] = "40"
        var["current"] = {
            "selected": False,
            "text": "40",
            "value": "40"
        }
        var["options"] = [
            {
                "selected": True,
                "text": "40",
                "value": "40"
            }
        ]
        updated = True
    elif var.get("name") == "max_pct":
        print("Updating max_pct to 70...")
        var["query"] = "70"
        var["current"] = {
            "selected": False,
            "text": "70",
            "value": "70"
        }
        var["options"] = [
            {
                "selected": True,
                "text": "70",
                "value": "70"
            }
        ]
        updated = True

if updated:
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    print("Dashboard variables updated successfully in distribuidor_dashboard.json.")
else:
    print("Failed to find min_pct or max_pct in dashboard templating list.")
