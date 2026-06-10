import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Find Panel 15
panel_15 = None
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        panel_15 = panel
        break

if not panel_15:
    print("Panel 15 not found!")
    exit(1)

# 1. Update defaults thresholds steps
# Step 0 (Base): #E32636 (Red)
# Step 1: #2FD06A (Green)
# Step 2: #E32635 (Red - distinct hex)
panel_15['fieldConfig']['defaults']['thresholds']['steps'] = [
    {
        "color": "#E32636",
        "value": None
    },
    {
        "color": "#2FD06A",
        "value": 1.0
    },
    {
        "color": "#E32635",
        "value": 6.0
    }
]

# 2. Update configFromData mappings
for transform in panel_15.get('transformations', []):
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
            elif 'Max' in field_name:
                mapping['handlerKey'] = 'threshold2'
                mapping['handlerArguments'] = {
                    "threshold": {
                        "color": "#E32635"
                      }
                }

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Updated dashboard with distinct red hex #E32635 for Max thresholds.")
