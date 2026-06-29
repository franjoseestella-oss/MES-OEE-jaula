import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    pid = p.get('id')
    title = p.get('title')
    print(f"Panel ID: {pid} | Title: {title}")
    for t in p.get('targets', []):
        ref_id = t.get('refId')
        query = t.get('rawSql')
        print(f"  Target refId: {ref_id}")
        if query:
            # print first 3 lines of query
            lines = query.split('\n')
            for line in lines[:5]:
                print(f"    {line}")
            if len(lines) > 5:
                print("    ...")
        else:
            print("    No rawSql")
    print("-" * 50)
