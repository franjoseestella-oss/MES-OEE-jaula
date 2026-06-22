import json
import sys

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Title:", data.get("title"))
print("UID:", data.get("uid"))
for p in data.get("panels", []):
    print(f"ID: {p.get('id')} | Title: {p.get('title')} | Type: {p.get('type')}")
