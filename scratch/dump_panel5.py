import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

panel = next(p for p in db.get("panels", []) if p.get("id") == 5)
print(panel.get("targets", [])[0].get("rawSql"))
