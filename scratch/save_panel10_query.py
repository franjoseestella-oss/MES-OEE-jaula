import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

found = False
for panel in db.get("panels", []):
    if panel.get("id") == 10:
        for target in panel.get("targets", []):
            if target.get("refId") == "A":
                with open("scratch/panel10_query_full.sql", "w", encoding="utf-8") as fw:
                    fw.write(target.get("rawSql"))
                print("Saved full Panel 10 query to scratch/panel10_query_full.sql")
                found = True
                break

if not found:
    print("Panel 10 not found.")
