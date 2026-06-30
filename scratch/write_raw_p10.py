import json

path = r"grafana/provisioning/dashboards/plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            with open("scratch/panel_10_current_raw.sql", "w", encoding="utf-8") as out:
                out.write(t.get("rawSql", ""))
print("Written panel_10_current_raw.sql")
