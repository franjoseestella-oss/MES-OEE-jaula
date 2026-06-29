import json
import sys

sys.stdout.reconfigure(encoding='utf-8')


filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    pid = p.get('id')
    title = p.get('title')
    if pid in [7, 8]:
        print(f"\n========================================\nPanel ID: {pid} | Title: {title}\n========================================\n")
        for t in p.get('targets', []):
            ref_id = t.get('refId')
            query = t.get('rawSql')
            print(f"--- Target refId: {ref_id} ---")
            print(query)
            print()
