import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"grafana/provisioning/dashboards/plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print(f"======================= LOCAL PANEL 10: {p.get('title')} =======================")
        for t in p.get("targets", []):
            print(f"RefID: {t.get('refId')}")
            print(t.get("rawSql", ""))
            print("-" * 60)
