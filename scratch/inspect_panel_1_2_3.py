import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    panel_id = p.get("id")
    if panel_id in [1, 2, 3]:
        print(f"=== Panel {panel_id}: {p.get('title')} ===")
        if p.get("targets"):
            print(p["targets"][0].get("rawSql"))
        print("\n")
