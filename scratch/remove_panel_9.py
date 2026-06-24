import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

panels = data.get("panels", [])
new_panels = []
removed = False
updated_panel_10 = False

for panel in panels:
    pid = panel.get("id")
    if pid == 9:
        print(f"Removing Panel 9: '{panel.get('title')}'")
        removed = True
        continue
    
    if pid == 10:
        print(f"Updating Panel 10: '{panel.get('title')}'")
        panel["gridPos"] = {
            "h": 28,
            "w": 24,
            "x": 0,
            "y": 20
        }
        updated_panel_10 = True
    
    new_panels.append(panel)

data["panels"] = new_panels

if removed and updated_panel_10:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully updated plan_dashboard.json")
else:
    print(f"Error: removed={removed}, updated_panel_10={updated_panel_10}")
