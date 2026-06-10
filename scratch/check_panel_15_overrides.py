import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        field_config = panel.get('fieldConfig', {})
        print("defaults thresholds:", json.dumps(field_config.get('defaults', {}).get('thresholds'), indent=2))
        print("overrides:", json.dumps(field_config.get('overrides'), indent=2))
