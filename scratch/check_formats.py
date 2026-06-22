import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

formats = set()
for p in dash.get("panels", []):
    for target in p.get("targets", []):
        formats.add(target.get("format"))

print("Formats found in dashboard:", formats)
