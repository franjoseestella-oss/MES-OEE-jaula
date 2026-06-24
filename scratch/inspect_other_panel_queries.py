import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for pid in [1, 2, 3]:
    for panel in data.get("panels", []):
        if panel.get("id") == pid:
            print(f"\n=== Panel {pid}: {panel.get('title')} ===")
            targets = panel.get("targets", [])
            if targets:
                print(targets[0].get("rawSql"))
