import json
with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("Title:", d.get("title"))
panels = d.get("panels", [])
print(f"Found {len(panels)} panels.")
for p in panels:
    print(f"Panel ID: {p.get('id')}, Title: {p.get('title')}")
    targets = p.get("targets", [])
    for idx, t in enumerate(targets):
        raw_sql = t.get("rawSql", "")
        if raw_sql:
            print(f"  Target {idx} rawSql length: {len(raw_sql)}")
            if "AlarmIntervals" in raw_sql or "ActiveSlotIdx" in raw_sql:
                print("  --> Found matching query here!")
