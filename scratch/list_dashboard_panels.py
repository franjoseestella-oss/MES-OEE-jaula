import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

print(f"Dashboard Title: {db.get('title')}")
print(f"Dashboard UID: {db.get('uid')}")

def inspect_panel(panel, prefix=""):
    pid = panel.get("id")
    title = panel.get("title")
    ptype = panel.get("type")
    print(f"{prefix}Panel ID: {pid} | Title: {title} | Type: {ptype}")
    targets = panel.get("targets", [])
    for idx, target in enumerate(targets):
        ref = target.get("refId")
        sql = target.get("rawSql")
        sql_snippet = (sql[:100] + "...") if sql else "None"
        print(f"{prefix}  Target {ref}: {sql_snippet}")
    
    # Check nested panels (e.g. in rows)
    for subpanel in panel.get("panels", []):
        inspect_panel(subpanel, prefix + "  ")

for panel in db.get("panels", []):
    inspect_panel(panel)
