import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for pid in [1, 2, 3]:
    panel = next(p for p in db.get("panels", []) if p.get("id") == pid)
    print(f"=====================================")
    print(f"PANEL ID: {pid} - {panel.get('title')}")
    print(f"=====================================")
    for idx, target in enumerate(panel.get("targets", [])):
        print(f"Target {idx} (refId: {target.get('refId')}):")
        print(target.get("rawSql", ""))
        print("-" * 50)
