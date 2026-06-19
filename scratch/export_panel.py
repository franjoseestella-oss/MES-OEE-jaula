import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("title") == "LISTADO DE SECUENCIAS (PLAN vs REAL)":
        with open("scratch/sequence_panel.json", "w", encoding="utf-8") as out:
            json.dump(panel, out, indent=2)
        print("Exported sequence panel to scratch/sequence_panel.json")
        break
else:
    print("Panel not found")
