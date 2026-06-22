import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 4:
        print(f"=== Panel {p.get('id')}: {p.get('title')} ===")
        for idx, t in enumerate(p.get("targets", [])):
            print(f"--- TARGET {t.get('refId')} ---")
            print(t.get("rawSql"))
            print("\n")
