import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"grafana/provisioning/dashboards/plan_dashboard.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

panels = data.get("panels", [])
for p in panels:
    if p.get("id") == 10:
        print(json.dumps(p, indent=2, ensure_ascii=False))
        break
else:
    print("Panel 10 not found.")
