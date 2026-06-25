import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

panel_5 = next(p for p in db.get("panels", []) if p.get("id") == 5)
with open("scratch/panel_5_raw.json", "w", encoding="utf-8") as out:
    json.dump(panel_5, out, indent=2, ensure_ascii=False)
