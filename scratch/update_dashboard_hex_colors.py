import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        for transform in panel.get('transformations', []):
            if transform.get('id') == 'configFromData':
                for mapping in transform.get('options', {}).get('mappings', []):
                    color = mapping.get('handlerArguments', {}).get('threshold', {}).get('color')
                    if color == 'green':
                        mapping['handlerArguments']['threshold']['color'] = '#2FD06A'
                        print(f"Updated {mapping.get('fieldName')} green to #2FD06A")
                    elif color == 'red':
                        mapping['handlerArguments']['threshold']['color'] = '#E32636'
                        print(f"Updated {mapping.get('fieldName')} red to #E32636")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Dashboard colors updated successfully.")
