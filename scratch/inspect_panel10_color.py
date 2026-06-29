import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    if p.get("id") == 10:
        print("Panel 10 options/fieldConfig:")
        print(json.dumps(p.get("fieldConfig", {}), indent=2))
        print("Panel 10 options:")
        print(json.dumps(p.get("options", {}), indent=2))
