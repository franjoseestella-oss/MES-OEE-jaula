import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            if t.get("refId") == "A":
                with open("scratch/panel_10_sql_dump.sql", "w", encoding="utf-8") as out:
                    out.write(t.get("rawSql"))
                print("Dumped query successfully")
