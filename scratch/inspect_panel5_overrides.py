import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 5:
        overrides = panel.get("fieldConfig", {}).get("overrides", [])
        for o in overrides:
            if o.get("matcher", {}).get("options") == "Estado":
                print(json.dumps(o, indent=2))
