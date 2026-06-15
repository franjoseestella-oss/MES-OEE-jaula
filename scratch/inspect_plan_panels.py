import json

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(dashboard_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Title:", data.get("title"))
print("UID:", data.get("uid"))
for panel in data.get("panels", []):
    print(f"Panel ID: {panel.get('id')} - Title: {panel.get('title')} - Type: {panel.get('type')}")
