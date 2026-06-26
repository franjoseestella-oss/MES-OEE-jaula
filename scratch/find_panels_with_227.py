import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    pid = panel.get("id")
    title = panel.get("title")
    for target in panel.get("targets", []):
        sql = target.get("sql", {}).get("rawSql") or target.get("rawSql")
        if sql and "227" in sql:
            print(f"Panel ID: {pid} | Title: {title} | Target: {target.get('refId')}")
    for subpanel in panel.get("panels", []):
        sub_id = subpanel.get("id")
        sub_title = subpanel.get("title")
        for target in subpanel.get("targets", []):
            sql = target.get("sql", {}).get("rawSql") or target.get("rawSql")
            if sql and "227" in sql:
                print(f"Sub-Panel ID: {sub_id} | Title: {sub_title} | Target: {target.get('refId')}")
