import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"grafana/provisioning/dashboards/plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            lines = t.get("rawSql", "").splitlines()
            print("\n".join(lines[:120]))
