import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 10:
        print("Panel 10 Title:", panel.get("title"))
        for target in panel.get("targets", []):
            print("--- Target ---")
            print(target.get("rawSql"))
