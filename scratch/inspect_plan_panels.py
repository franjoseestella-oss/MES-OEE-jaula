import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for i, panel in enumerate(data.get("panels", [])):
    print(f"Panel {i}: ID={panel.get('id')}, Title='{panel.get('title')}', Type='{panel.get('type')}'")
