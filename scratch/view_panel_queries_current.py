import json
import sys

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    pid = p.get("id")
    if pid in [5, 10]:
        print(f"======================= PANEL {pid}: {p.get('title')} =======================")
        for t in p.get("targets", []):
            print(f"RefID: {t.get('refId')}")
            print(t.get("rawSql", ""))
            print("-" * 60)
