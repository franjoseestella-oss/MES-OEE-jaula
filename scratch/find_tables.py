import json
import re

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

tables = set()
for p in data.get("panels", []):
    for t in p.get("targets", []):
        sql = t.get("rawSql", "")
        # Find matches for FROM or JOIN
        for match in re.findall(r'(?:from|join)\s+([a-zA-Z0-9_\.\[\]]+)', sql, re.IGNORECASE):
            tables.add(match.upper())

print("Tables found in SQL queries:")
for t in sorted(tables):
    print(f"  {t}")
