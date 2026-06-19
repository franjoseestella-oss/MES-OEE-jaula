import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"


with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Dashboard Title: {data.get('title')}")
for panel in data.get("panels", []):
    print(f"\nPanel ID: {panel.get('id')} | Title: {panel.get('title')}")
    for target in panel.get("targets", []):
        print(f"  RefId: {target.get('refId')}")
        print("  Query:")
        print(target.get("rawSql"))
