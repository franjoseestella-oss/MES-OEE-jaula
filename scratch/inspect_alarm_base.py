import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

raw_sql = ""
for p in dash.get("panels", []):
    if p.get("id") == 10:
        raw_sql = p["targets"][0]["rawSql"]
        break

lines = raw_sql.split("\n")
for i, line in enumerate(lines):
    if "AlarmBase AS" in line:
        start = max(0, i - 1)
        end = min(len(lines), i + 25)
        for j in range(start, end):
            print(f"Line {j}: {lines[j]}")
        break
