import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    print(f"ID: {panel.get('id')} | Title: {panel.get('title')} | Type: {panel.get('type')} | GridPos: {panel.get('gridPos')}")
