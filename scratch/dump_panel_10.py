import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

panel_10 = next(p for p in db.get("panels", []) if p.get("id") == 10)
with open("scratch/panel_10_raw.json", "w", encoding="utf-8") as out:
    json.dump(panel_10, out, indent=2, ensure_ascii=False)
