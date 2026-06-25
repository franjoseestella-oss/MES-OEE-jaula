import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    title = panel.get("title")
    pid = panel.get("id")
    for t in panel.get("targets", []):
        raw_sql = t.get("rawSql")
        if raw_sql:
            print(f"Panel ID {pid} ({title}):")
            if "$__timeFilter" in raw_sql:
                print("  FOUND $__timeFilter in SQL:")
                print(raw_sql)
                print("-" * 50)
