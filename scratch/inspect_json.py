import json
import sys

# Set standard output encoding to utf-8 if possible
sys.stdout.reconfigure(encoding='utf-8')

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Title:", data.get("title"))
print("Dashboard UID:", data.get("uid"))
print("Number of panels:", len(data.get("panels", [])))
for i, panel in enumerate(data.get("panels", [])):
    title = panel.get('title', '').encode('ascii', 'replace').decode('ascii')
    print(f"\nPanel {i+1}: ID={panel.get('id')} Title={title} Type={panel.get('type')}")
    targets = panel.get("targets", [])
    for j, target in enumerate(targets):
        sql = target.get("rawSql")
        print(f"  Target {j+1}:")
        if sql:
            # print first 3 lines of sql
            lines = sql.split('\n')
            for line in lines:
                print(f"    {line}")
        else:
            print("    No rawSql")
