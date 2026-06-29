import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    if p.get("id") == 5:
        print("Panel 5 targets:")
        for t in p.get("targets", []):
            print(t.get("rawSql"))
