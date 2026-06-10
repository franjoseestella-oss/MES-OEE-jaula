import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    if p.get("id") == 14:
        print(json.dumps(p, indent=2))
        break
