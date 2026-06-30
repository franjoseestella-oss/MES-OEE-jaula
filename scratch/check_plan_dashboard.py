import json

with open(r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

print("Dashboard Title:", db.get("title"))
print("Dashboard Time:", db.get("time"))

for panel in db.get("panels", []):
    print(f"\nPanel ID: {panel.get('id')} | Title: {panel.get('title')} | Type: {panel.get('type')}")
    print("  timeFrom:", panel.get("timeFrom"))
    print("  timeShift:", panel.get("timeShift"))
    print("  hideTimepicker:", panel.get("hideTimepicker"))
