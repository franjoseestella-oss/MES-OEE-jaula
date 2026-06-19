import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION%20MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json".replace("%20", " ")

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    if "LISTADO DE SECUENCIAS" in panel.get("title", ""):
        print(f"Panel Title: {panel['title']}")
        print(f"Panel Type: {panel['type']}")
        for target in panel.get("targets", []):
            print("--- Target Query ---")
            print(target.get("rawSql"))
