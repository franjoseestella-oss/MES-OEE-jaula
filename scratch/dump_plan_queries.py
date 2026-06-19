import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    title = panel.get("title", "")
    pid = panel.get("id")
    print(f"Panel ID: {pid} - Title: {title}")
    for idx, target in enumerate(panel.get("targets", [])):
        raw_sql = target.get("rawSql", "")
        if raw_sql:
            print(f"  Target {idx} (refId: {target.get('refId')}):")
            print("-" * 40)
            print(raw_sql[:300] + "...")
            print("-" * 40)
