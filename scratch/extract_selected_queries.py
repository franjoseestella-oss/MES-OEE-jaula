import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION%20MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json".replace("%20", " ")

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel_id in [1, 2, 3, 4]:
    panel = next(p for p in db.get("panels", []) if p.get("id") == panel_id)
    print(f"\n==========================================")
    print(f"ID: {panel.get('id')} | Title: {panel.get('title')}")
    print(f"==========================================")
    for idx, target in enumerate(panel.get("targets", [])):
        refId = target.get("refId", f"Target_{idx}")
        print(f"--- RefID: {refId} ---")
        print(target.get("rawSql"))
