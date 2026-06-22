import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    targets = p.get("targets", [])
    if not targets:
        continue
    sql = targets[0].get("rawSql", "")
    print(f"=== Panel {p.get('id')}: {p.get('title')} ===")
    print(sql[:400] + ("..." if len(sql) > 400 else ""))
    print()
