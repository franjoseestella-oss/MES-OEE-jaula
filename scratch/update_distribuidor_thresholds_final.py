import json
import os

dashboard_path = os.path.abspath(r"grafana/provisioning/dashboards/distribuidor_dashboard.json")

print(f"Reading from: {dashboard_path}")
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

# 1. Update min_pct and max_pct variables
for var in dashboard.get("templating", {}).get("list", []):
    if var.get("name") == "min_pct":
        print("Updating min_pct variable...")
        var["current"] = {
            "selected": False,
            "text": "40",
            "value": "40"
        }
        var["options"] = [
            {
                "selected": True,
                "text": "40",
                "value": "40"
            }
        ]
        var["query"] = "40"
    elif var.get("name") == "max_pct":
        print("Updating max_pct variable...")
        var["current"] = {
            "selected": False,
            "text": "70",
            "value": "70"
        }
        var["options"] = [
            {
                "selected": True,
                "text": "70",
                "value": "70"
            }
        ]
        var["query"] = "70"

# 2. Update panels configuration
target_panel_ids = [102, 104, 106, 111, 113, 115]

for panel in dashboard.get("panels", []):
    pid = panel.get("id")
    if pid in target_panel_ids:
        print(f"Updating Panel {pid}: {panel.get('title')}")
        
        if "fieldConfig" not in panel:
            panel["fieldConfig"] = {}
        if "defaults" not in panel["fieldConfig"]:
            panel["fieldConfig"]["defaults"] = {}
            
        panel["fieldConfig"]["defaults"]["min"] = 0
        panel["fieldConfig"]["defaults"]["max"] = 100
        
        # We need three steps:
        # Base: #E32636 (Red) for values under min (0 to 40)
        # Step 1: #2FD06A (Green) starting at 40 (threshold_min)
        # Step 2: #E32636 (Red) starting at 70 (threshold_max)
        panel["fieldConfig"]["defaults"]["thresholds"] = {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},
                {"color": "#2FD06A", "value": 40.0},
                {"color": "#E32636", "value": 70.0}
            ]
        }
        
        # Enable showing threshold markers and labels in the gauge configuration
        if "options" not in panel:
            panel["options"] = {}
        panel["options"]["showThresholdMarkers"] = True
        panel["options"]["showThresholdLabels"] = True
        
        # Verify and fix mappings in configFromData
        if "transformations" in panel:
            for transform in panel["transformations"]:
                if transform.get("id") == "configFromData":
                    transform["options"] = {
                        "configRefId": "A",
                        "mappings": [
                            {
                                "fieldName": "threshold_min",
                                "handlerArguments": {
                                    "threshold": {
                                        "color": "#2FD06A"
                                    }
                                },
                                "handlerKey": "threshold1"
                            },
                            {
                                "fieldName": "threshold_max",
                                "handlerArguments": {
                                    "threshold": {
                                        "color": "#E32636"
                                    }
                                },
                                "handlerKey": "threshold2"
                            }
                        ]
                    }

with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print("Finished updating dashboard json file.")
