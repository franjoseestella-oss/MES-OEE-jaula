import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 4:
        for t in p.get("targets", []):
            with open(f"scratch/panel4_{t.get('refId')}.sql", "w", encoding="utf-8") as out:
                out.write(t.get("rawSql", ""))
    elif p.get("id") == 10:
        for t in p.get("targets", []):
            with open(f"scratch/panel10_{t.get('refId')}.sql", "w", encoding="utf-8") as out:
                out.write(t.get("rawSql", ""))

print("Exported SQL files to scratch/")
