import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Set dashboard version
d['version'] = 203

# Target panel 15
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        # Standard options
        panel['fieldConfig']['defaults']['min'] = 0
        panel['fieldConfig']['defaults']['max'] = 8
        panel['fieldConfig']['defaults']['decimals'] = 2
        panel['fieldConfig']['defaults']['unit'] = 's'
        panel['fieldConfig']['defaults']['color'] = { "mode": "thresholds" }
        
        # Default thresholds
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#E32636",  # Red (Base)
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Green (Step 1)
                    "value": 3
                },
                {
                    "color": "#E32636",  # Red (Step 2)
                    "value": 5
                }
            ]
        }
        
        # Clean and reconstruct transformations
        gauges = [
            ("Elevación Sin Carga", "Elevación Sin Carga Min", "Elevación Sin Carga Max"),
            ("Descenso Sin Carga", "Descenso Sin Carga Min", "Descenso Sin Carga Max"),
            ("Elevación Con Carga", "Elevación Con Carga Min", "Elevación Con Carga Max"),
            ("Descenso Con Carga", "Descenso Con Carga Min", "Descenso Con Carga Max")
        ]
        
        transformations = []
        for gauge_name, min_field, max_field in gauges:
            transformations.append({
                "id": "configFromData",
                "options": {
                    "applyTo": {
                        "id": "byName",
                        "options": gauge_name
                    },
                    "configRefId": "A",
                    "mappings": [
                        {
                            "fieldName": min_field,
                            "handlerKey": "threshold1",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"  # Green
                                }
                            }
                        },
                        {
                            "fieldName": max_field,
                            "handlerKey": "threshold1",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"  # Red
                                }
                            }
                        }
                    ]
                }
            })
            
        # Add the filter fields by name transformation at the end
        transformations.append({
            "id": "filterFieldsByName",
            "options": {
                "include": {
                    "names": [g[0] for g in gauges]
                }
            }
        })
        
        panel['transformations'] = transformations
        print("Panel 15 reconstructed successfully.")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Saved reconstructed dashboard to file.")
