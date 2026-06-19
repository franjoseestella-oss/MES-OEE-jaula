import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("title") == "LISTADO DE SECUENCIAS (PLAN vs REAL)":
        print("Panel Title:", panel.get("title"))
        print("Panel ID:", panel.get("id"))
        for target in panel.get("targets", []):
            print("Query (rawSql):")
            print(target.get("rawSql"))
