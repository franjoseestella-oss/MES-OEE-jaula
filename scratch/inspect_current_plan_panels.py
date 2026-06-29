import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

panels = dashboard.get("panels", [])

print(f"Dashboard Title: {dashboard.get('title')}")
for p in panels:
    pid = p.get('id')
    title = p.get('title')
    ptype = p.get('type')
    print(f"PANEL ID: {pid} | Title: {title} | Type: {ptype}")
