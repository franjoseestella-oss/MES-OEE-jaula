import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    print(f"Panel ID: {p.get('id')}, Title: {p.get('title')}, Type: {p.get('type')}")
    # Check if rawSql exists and contains s.planned_start
    targets = p.get("targets", [])
    if targets and "rawSql" in targets[0]:
        sql = targets[0]["rawSql"]
        if "FilteredTimestamps" in sql:
            print("  -> Contains FilteredTimestamps")
        if "s.actual_start" in sql:
            print("  -> Contains s.actual_start")
