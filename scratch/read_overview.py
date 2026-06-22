import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
try:
    with open(filepath, "r", encoding="utf-8") as f:
        db = json.load(f)
except Exception as e:
    print(f"Error: {e}")
    db = {}

panels = {p.get("id"): p for p in db.get("panels", [])}

for pid in [9, 10]:
    p = panels.get(pid)
    if p:
        print(f"=== PANEL {pid}: '{p.get('title')}' ===")
        print(f"Type: {p.get('type')}")
        print(f"GridPos: {p.get('gridPos')}")
        targets = p.get("targets", [])
        print(f"Targets count: {len(targets)}")
        for idx, t in enumerate(targets):
            print(f"  Target {idx} (RefId: {t.get('refId')}):")
            print(f"    RawSql: {t.get('rawSql')}")
            print(f"    Format: {t.get('format')}")
        # Let's print panel options or display mode if present
        options = p.get("options", {})
        print(f"  Options: {json.dumps(options, indent=2)}")
    else:
        print(f"Panel {pid} not found in plan_dashboard.json")
