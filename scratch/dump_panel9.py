import json
import sys

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

p9 = [p for p in data.get('panels', []) if p.get('id') == 9][0]

with open(r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\panel9_details.json", "w", encoding="utf-8") as f:
    json.dump(p9, f, indent=2, ensure_ascii=False)

print("Panel 9 details written to scratch/panel9_details.json")
