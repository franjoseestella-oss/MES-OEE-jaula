import json

dashboard_path = 'grafana/provisioning/dashboards/oee_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Increment dashboard version
if 'version' in d:
    d['version'] += 1

panels_updated = 0

for panel in d.get('panels', []):
    panel_id = panel.get('id')
    if panel_id in (14, 15):
        # 1. Update defaults thresholds to 3-step format
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#E32636",  # Red for below min
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Green for normal range
                    "value": 3.0
                },
                {
                    "color": "#E32636",  # Red for above max
                    "value": 5.0
                }
            ]
        }
        
        # 2. Correctly set transformations mappings
        transformations = panel.get('transformations', [])
        for transform in transformations:
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
                        print(f"Panel {panel_id}: Mapped {field_name} -> threshold1 (Green)")
                    elif 'Max' in field_name:
                        mapping['handlerKey'] = 'threshold2'
                        mapping['handlerArguments'] = {
                            "threshold": {
                                "color": "#E32636"
                            }
                        }
                        print(f"Panel {panel_id}: Mapped {field_name} -> threshold2 (Red)")
        panels_updated += 1

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Finished! Updated {panels_updated} panels in {dashboard_path}")
