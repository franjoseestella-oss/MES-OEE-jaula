import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

count = 0
for p in data.get("panels", []):
    for t in p.get("targets", []):
        sql = t.get("rawSql", "")
        if "CAST($__timeFrom() AS DATE)" in sql:
            new_sql = sql.replace(
                "CAST($__timeFrom() AS DATE)",
                "CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE)"
            )
            t["rawSql"] = new_sql
            count += 1

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated {count} targets in plan_dashboard.json")
