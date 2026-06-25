import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 1:
        print(json.dumps(panel, indent=2, ensure_ascii=False))
        break
