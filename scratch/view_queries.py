import json
import sys

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

output_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\all_queries.txt"
with open(output_path, 'w', encoding='utf-8') as outf:
    for p in data.get('panels', []):
        pid = p.get('id')
        title = p.get('title', '')
        outf.write(f"\n==================================================\n")
        outf.write(f"Panel ID {pid}: {title} ({p.get('type')})\n")
        outf.write(f"==================================================\n")
        targets = p.get('targets', [])
        for idx, t in enumerate(targets):
            sql = t.get('rawSql', t.get('query', ''))
            outf.write(f"--- Target {idx} (Ref {t.get('refId')}): ---\n")
            outf.write(sql + "\n")
