import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    pid = panel.get("id")
    title = panel.get("title")
    for t in panel.get("targets", []):
        sql = t.get("rawSql", "")
        if "@EvalTime" in sql:
            print(f"Panel {pid}: '{title}' contains @EvalTime")
