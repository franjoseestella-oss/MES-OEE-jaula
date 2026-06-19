import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for i, panel in enumerate(db.get("panels", [])):
    if "listado de secuencias" in panel.get("title", "").lower():
        print(f"Panel Index: {i} | Title: '{panel.get('title')}'")
        for target in panel.get("targets", []):
            print(f"RefId: {target.get('refId')}")
            print(f"Query:\n{target.get('rawSql')}")
