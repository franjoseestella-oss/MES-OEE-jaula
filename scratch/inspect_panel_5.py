import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("id") == 5:
        print(json.dumps(panel, indent=2, ensure_ascii=False)[:3000])
