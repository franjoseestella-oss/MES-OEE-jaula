import json
db_path = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 10:
        print(f"Panel ID: {p.get('id')}")
        print(f"Title: {p.get('title')}")
        for t in p.get("targets", []):
            print(f"Target RefId: {t.get('refId')}")
            print(t.get("rawSql")[:2000])
            print("...")
            print(t.get("rawSql")[-2000:])
