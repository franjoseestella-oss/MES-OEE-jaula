import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 14:
        print("Panel 14 Targets:")
        for target in p.get("targets", []):
            print(target.get("rawSql"))
        print("Panel 14 Transformations:")
        for t in p.get("transformations", []):
            print(json.dumps(t, indent=2))

    if p.get("id") == 15:
        print("Panel 15 Targets:")
        for target in p.get("targets", []):
            print(target.get("rawSql"))
        print("Panel 15 Transformations:")
        for t in p.get("transformations", []):
            print(json.dumps(t, indent=2))
