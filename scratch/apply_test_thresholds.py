import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Increment dashboard version
d['version'] = 202

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Default limits
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        
        # Defaults thresholds: Base (Red), Step 1 (Green), Step 2 (Red)
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#E32636",  # Red
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Green
                    "value": 3
                },
                {
                    "color": "#E32636",  # Red
                    "value": 5
                }
            ]
        }
        
        # Mappings: Min -> threshold1 (Red), Max -> threshold1 (Green)
        for transform in panel.get('transformations', []):
            if transform.get('id') == 'configFromData':
                mappings = transform.get('options', {}).get('mappings', [])
                # Rebuild mappings to ensure only Min and Max are mapped to threshold1
                new_mappings = []
                for mapping in mappings:
                    field_name = mapping.get('fieldName', '')
                    if 'Min' in field_name:
                        new_mappings.append({
                            "fieldName": field_name,
                            "handlerKey": "threshold1",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"  # Red
                                }
                            }
                        })
                    elif 'Max' in field_name:
                        new_mappings.append({
                            "fieldName": field_name,
                            "handlerKey": "threshold1",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"  # Green
                                }
                            }
                        })
                transform['options']['mappings'] = new_mappings

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Test threshold mappings (Min -> Red, Max -> Green) applied to dashboard JSON.")
