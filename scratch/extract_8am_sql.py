import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if panel.get("id") == 10:
        sql = panel.get("targets", [])[0].get("rawSql")
        with open("scratch/panel_10_sql_8am.txt", "w", encoding="utf-8") as out:
            out.write(sql)
        print("Wrote panel_10_sql_8am.txt")
