import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 9:
        summary = {
            "type": p.get("type"),
            "title": p.get("title"),
            "gridPos": p.get("gridPos"),
            "fieldConfig": p.get("fieldConfig"),
            "options": p.get("options")
        }
        with open("scratch/panel_9_summary.json", "w", encoding="utf-8") as out:
            json.dump(summary, out, indent=2, ensure_ascii=False)
        print("Done! Check scratch/panel_9_summary.json")
        break
