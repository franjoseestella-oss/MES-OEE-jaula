import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        print(json.dumps(panel, indent=2))
