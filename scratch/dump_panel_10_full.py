import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        with open("scratch/panel_10_query_full.sql", "w", encoding="utf-8") as out:
            out.write(p["targets"][0]["rawSql"])
        print("Wrote complete SQL to scratch/panel_10_query_full.sql")
        break
