import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") in (5, 10):
        print(f"--- Panel {p.get('id')} ({p.get('title')}) ---")
        for t in p.get("targets", []):
            print(t.get("rawSql"))
            print("-" * 50)
