import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 15:
        print(json.dumps(p.get("fieldConfig", {}), indent=2, ensure_ascii=False))
        break
