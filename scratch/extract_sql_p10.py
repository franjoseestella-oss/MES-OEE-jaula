import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        print(f"Panel 10 Title: {p.get('title')}")
        with open("scratch/panel_10_sql.sql", "w", encoding="utf-8") as out:
            out.write(p.get("targets", [])[0].get("rawSql", ""))
        print("SQL saved to scratch/panel_10_sql.sql")
        break
