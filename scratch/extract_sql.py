import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            with open("scratch/panel_10_sql.sql", "w", encoding="utf-8") as out:
                out.write(t.get("rawSql", ""))
            print("Successfully wrote scratch/panel_10_sql.sql")
