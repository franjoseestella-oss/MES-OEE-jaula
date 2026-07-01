import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    print(f"ID {p.get('id')}: {p.get('title')} -> gridPos: {p.get('gridPos')}")
