import json
import sys

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    if p.get("id") == 10:
        sql = p.get("targets", [])[0].get("rawSql")
        with open("scratch/panel10_query_full.sql", "w", encoding="utf-8") as out:
            out.write(sql)
        print("Successfully wrote full Panel 10 query to scratch/panel10_query_full.sql")
