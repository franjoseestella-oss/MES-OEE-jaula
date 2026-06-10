import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

for p in d.get('panels', []):
     print(f"ID {p.get('id')}: {p.get('title')} (Type: {p.get('type')})")
