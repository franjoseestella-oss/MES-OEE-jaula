import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

ids = []
for p in db.get("panels", []):
    ids.append(p.get("id"))
    if p.get("id") == 9:
        print("Panel 9 title:", p.get("title"))
        print("Panel 9 gridPos:", p.get("gridPos"))
print("All existing panel IDs:", sorted(ids))
