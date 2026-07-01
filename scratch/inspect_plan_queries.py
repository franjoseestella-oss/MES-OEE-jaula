import json
import os

os.makedirs("scratch/panel_queries", exist_ok=True)
path = r"grafana/provisioning/dashboards/plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    pid = p.get("id")
    if pid in [1, 4, 5, 10]:
        print(f"Panel {pid}: {p.get('title')}")
        for idx, target in enumerate(p.get("targets", [])):
            sql = target.get("rawSql")
            if sql:
                filename = f"scratch/panel_queries/panel_{pid}_target_{idx}.sql"
                with open(filename, "w", encoding="utf-8") as out:
                    out.write(sql)
                print(f"  Wrote target {idx} to {filename}")
