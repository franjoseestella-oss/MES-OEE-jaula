import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Increment dashboard version
d['version'] = 201

for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Keep min=0 and max=8
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        
        # Set the default thresholds to: Base (Red), Step 1 (Green), Step 2 (Red)
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#E32636",  # Red for below min
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Green for normal range
                    "value": 3
                },
                {
                    "color": "#E32636",  # Red for above max
                    "value": 5
                }
            ]
        }
        
        # Correctly set transformations mappings
        for transform in panel.get('transformations', []):
            if transform.get('id') == 'configFromData':
                mappings = transform.get('options', {}).get('mappings', [])
                for mapping in mappings:
                    field_name = mapping.get('fieldName', '')
                    if 'Min' in field_name:
                        mapping['handlerKey'] = 'threshold1'
                        mapping['handlerArguments'] = {
                            "threshold": {
                                "color": "#2FD06A"
                            }
                        }
                        print(f"Mapped {field_name} -> threshold1 (#2FD06A)")
                    elif 'Max' in field_name:
                        mapping['handlerKey'] = 'threshold2'
                        mapping['handlerArguments'] = {
                            "threshold": {
                                "color": "#E32636"
                            }
                        }
                        print(f"Mapped {field_name} -> threshold2 (#E32636)")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Corrected threshold mappings applied to dashboard JSON.")
