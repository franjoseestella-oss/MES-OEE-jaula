import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        print(f"Panel 10 Title: {p.get('title')}")
        print("Panel 10 targets:")
        for t in p.get("targets", []):
            print(f"RefId: {t.get('refId')}")
            print("Query:")
            print(t.get("rawSql"))
        break
