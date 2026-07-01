import json
import sys

# Force stdout to use utf-8 to avoid CP1252 encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Dashboard Title: {data.get('title')}")
print(f"Dashboard UID: {data.get('uid')}")
print(f"Time: {data.get('time')}")
print(f"Timepicker hidden: {data.get('timepicker', {}).get('hidden')}")
print("Templating variables:")
for var in data.get('templating', {}).get('list', []):
    print(f"  - Name: {var.get('name')}, Type: {var.get('type')}, Label: {var.get('label')}, Query: {var.get('query')}")

print("\nPanels:")
for p in data.get('panels', []):
    title = p.get('title', '')
    print(f"Panel ID {p.get('id')}: {title} ({p.get('type')})")
    targets = p.get('targets', [])
    for idx, t in enumerate(targets):
        sql = t.get('rawSql', t.get('query', ''))
        first_lines = "\n".join(sql.strip().split("\n")[:3])
        print(f"  Target {idx} (Ref {t.get('refId')}):")
        print(f"    {first_lines} ...")
