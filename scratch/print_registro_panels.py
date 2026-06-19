import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for i, panel in enumerate(data.get("panels", [])):
    print(f"Panel ID={panel.get('id')} Title={panel.get('title')}")
    for target in panel.get("targets", []):
        print(target.get("rawSql"))
    print("-" * 40)
