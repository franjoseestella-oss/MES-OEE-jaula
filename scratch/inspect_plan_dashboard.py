import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    if p.get('id') == 10:
        print(json.dumps(p, indent=2)[:2000])
