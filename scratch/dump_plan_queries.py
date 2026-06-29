import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

lines = []
for panel in db.get("panels", []):
    title = panel.get("title", "")
    pid = panel.get("id")
    lines.append(f"Panel ID: {pid} - Title: {title}")
    for idx, target in enumerate(panel.get("targets", [])):
        raw_sql = target.get("rawSql", "")
        if raw_sql:
            lines.append(f"  Target {idx} (refId: {target.get('refId')}):")
            lines.append("-" * 40)
            lines.append(raw_sql)
            lines.append("-" * 40)

with open("scratch/all_plan_queries_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

