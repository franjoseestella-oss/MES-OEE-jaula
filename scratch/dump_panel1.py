import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

panel = next(p for p in db.get("panels", []) if p.get("id") == 1)
print(panel.get("targets", [])[0].get("rawSql", ""))
