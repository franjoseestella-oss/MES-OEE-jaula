import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("id") == 4:
        targets = panel.get("targets", [])
        for t in targets:
            print(f"--- RefId: {t.get('refId')} ---")
            print(t.get("rawSql"))
