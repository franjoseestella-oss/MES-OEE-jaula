import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("id") == 16:
        print(json.dumps(panel, indent=2))
        break
