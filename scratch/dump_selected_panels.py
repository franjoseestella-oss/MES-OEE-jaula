import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") in [4, 10]:
        print(f"=== Panel {p.get('id')}: {p.get('title')} ===")
        # Print basic panel configurations, omitting the target query itself
        for k, v in p.items():
            if k != "targets":
                print(f"  {k}: {repr(v)[:150]}")
        print()
