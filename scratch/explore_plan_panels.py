import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

with open("scratch/full_panels_dump.txt", "w", encoding="utf-8") as out:
    out.write("Title: " + str(db.get("title")) + "\n")
    out.write("Time range: " + json.dumps(db.get("time")) + "\n")

    def check_panels(panels):
        for p in panels:
            out.write(f"\n--- Panel ID: {p.get('id')} | Title: {p.get('title')} | Type: {p.get('type')} ---\n")
            if "targets" in p:
                for t in p["targets"]:
                    out.write(f"Target {t.get('refId')}:\n")
                    sql = t.get("rawSql") or t.get("sql")
                    if isinstance(sql, dict):
                        out.write(json.dumps(sql, indent=2) + "\n")
                    else:
                        out.write(str(sql) + "\n")
            if "panels" in p:
                check_panels(p["panels"])

    if "panels" in db:
        check_panels(db["panels"])
