import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Update min and max limits to 0 and 8
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        
        # Update transformation mappings: all thresholds should use handlerKey: "threshold1"
        for transform in panel.get('transformations', []):
            if transform.get('id') == 'configFromData':
                for mapping in transform.get('options', {}).get('mappings', []):
                    if mapping.get('handlerKey') == 'threshold2':
                        mapping['handlerKey'] = 'threshold1'
                        print(f"Updated mapping for {mapping.get('fieldName')} to threshold1")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Dashboard successfully updated.")
