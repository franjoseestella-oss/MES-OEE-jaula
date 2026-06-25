import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for pid_to_inspect in [1, 3, 5]:
    for panel in db.get("panels", []):
        if panel.get("id") == pid_to_inspect:
            print(f"=== PANEL {pid_to_inspect} ({panel.get('title')}) ===")
            for t in panel.get("targets", []):
                print(t.get("rawSql"))
            print("-" * 60)
