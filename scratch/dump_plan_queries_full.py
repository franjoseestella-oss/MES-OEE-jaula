import json
import sys

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

with open("scratch/plan_queries_dump.txt", "w", encoding="utf-8") as out:
    for p in db.get("panels", []):
        targets = p.get("targets", [])
        if not targets:
            continue
        sql = targets[0].get("rawSql", "")
        out.write(f"=== Panel {p.get('id')}: {p.get('title')} ===\n")
        out.write(sql)
        out.write("\n\n")

print("Dumped queries to scratch/plan_queries_dump.txt")
