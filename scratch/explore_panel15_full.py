import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

p15 = [p for p in d.get('panels', []) if p.get('id') == 15][0]
print(json.dumps(p15, indent=2))
