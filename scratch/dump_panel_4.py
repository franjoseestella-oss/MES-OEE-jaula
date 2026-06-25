import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

panel_4 = next(p for p in db.get("panels", []) if p.get("id") == 4)
with open("scratch/panel_4_raw.json", "w", encoding="utf-8") as out:
    json.dump(panel_4, out, indent=2, ensure_ascii=False)
