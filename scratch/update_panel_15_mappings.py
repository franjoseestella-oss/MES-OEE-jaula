import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Find Panel 15
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # We want to replace the transformations
        new_transforms = []
        for transform in panel.get('transformations', []):
            if transform.get('id') == 'configFromData':
                # Determine which field it applies to
                options = transform.get('options', {})
                apply_to = options.get('applyTo', {})
                field_name = apply_to.get('options') # e.g. "Elevación Sin Carga"
                
                if field_name:
                    # Rebuild mappings
                    new_mappings = [
                        {
                            "fieldName": f"{field_name} 1_Min",
                            "handlerKey": "threshold1",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            }
                        },
                        {
                            "fieldName": f"{field_name} 2_Max",
                            "handlerKey": "threshold2",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            }
                        }
                    ]
                    transform['options']['mappings'] = new_mappings
            new_transforms.append(transform)
        panel['transformations'] = new_transforms

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Successfully updated log_dashboard.json transformation mappings for panel 15.")
