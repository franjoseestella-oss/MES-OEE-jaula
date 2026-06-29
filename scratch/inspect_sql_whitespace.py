import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

raw_sql = dash["panels"][0]["targets"][0]["rawSql"]  # wait, panel with id 10 might not be the first one. Let's find it.
for p in dash.get("panels", []):
    if p.get("id") == 10:
        raw_sql = p["targets"][0]["rawSql"]
        break

lines = raw_sql.split("\n")
for i, line in enumerate(lines):
    if "COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)" in line:
        # Print 5 lines before and 10 lines after
        start = max(0, i - 2)
        end = min(len(lines), i + 12)
        for j in range(start, end):
            print(f"Line {j}: {repr(lines[j])}")
        break
