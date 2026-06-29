import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 title:", p.get("title"))
        print("Panel 10 type:", p.get("type"))
        print("Panel 10 queries:")
        for target in p.get("targets", []):
            print("Query ID:", target.get("refId"))
            print(target.get("rawSql") or target.get("expr"))
        print("\nPanel 10 fieldConfig options:")
        defaults = p.get("fieldConfig", {}).get("defaults", {})
        print("Mappings:", json.dumps(defaults.get("mappings", []), indent=2))
        print("Thresholds:", json.dumps(defaults.get("thresholds", {}), indent=2))
