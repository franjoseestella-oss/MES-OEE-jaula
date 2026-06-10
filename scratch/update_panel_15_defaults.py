import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Find Panel 15
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Set min/max to 0 and 8
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        
        # Set steps: Base (orange), Min (green), Max (red)
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#F4A623",
                    "value": None
                },
                {
                    "color": "#2FD06A",
                    "value": 3.0
                },
                {
                    "color": "#E32636",
                    "value": 5.0
                }
            ]
        }

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Successfully updated log_dashboard.json thresholds and limits for panel 15.")
