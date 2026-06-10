import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

for p in d.get('panels', []):
    if p.get('id') in [10, 11, 12, 13]:
         print(f"ID {p.get('id')}: {p.get('targets')[0].get('rawSql') if p.get('targets') else 'None'}")
