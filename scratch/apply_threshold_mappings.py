import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Let's locate panel 15 and modify its transformations
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Update the default limits to be min=0, max=8
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        
        # Ensure default thresholds steps has three steps with clean colors
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#F4A623",  # Base color for values below Min (Orange)
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Color for values between Min and Max (Green)
                    "value": 3
                },
                {
                    "color": "#E32636",  # Color for values above Max (Red)
                    "value": 5
                }
            ]
        }
        
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

print("Dashboard threshold mappings applied successfully.")
