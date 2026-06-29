import json

filepath = "grafana/provisioning/dashboards/turno_actual_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    pid = p.get('id')
    title = p.get('title')
    for t in p.get('targets', []):
        ref_id = t.get('refId')
        query = t.get('rawSql')
        if query and "$__timeFrom" in query:
            print(f"Panel ID: {pid} | Title: {title} | Ref: {ref_id}")
            for line in query.split('\n'):
                if "$__timeFrom" in line:
                    print(f"  MATCH: {line.strip()}")
