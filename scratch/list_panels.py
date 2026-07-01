import json
with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for p in data.get('panels', []):
    print(f"ID: {p.get('id')}, Title: {p.get('title')}, Type: {p.get('type')}")
