import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Let's find occurrences of "id": 7 and "id": 5
for idx, line in enumerate(lines):
    if '"id": 7' in line:
        print(f"Panel 7 ID at line {idx+1}")
    if '"id": 5' in line:
        print(f"Panel 5 ID at line {idx+1}")
    if 'dbo.CALENDARIO_LABORAL' in line:
        print(f"CALENDARIO_LABORAL at line {idx+1}")
