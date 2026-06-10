import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        print("Transformations:")
        print(json.dumps(panel.get('transformations'), indent=2))
