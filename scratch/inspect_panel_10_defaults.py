import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("id") == 10:
        print(json.dumps(panel.get("fieldConfig", {}).get("defaults", {}), indent=2, ensure_ascii=False))
        break
