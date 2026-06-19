import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for i, panel in enumerate(db.get("panels", [])):
    print(f"Panel {i} | Title: '{panel.get('title')}' | Type: '{panel.get('type')}' | gridPos: {panel.get('gridPos')}")
