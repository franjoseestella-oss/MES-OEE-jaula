import json

path = 'grafana/provisioning/dashboards/plan_dashboard.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for panel in data.get('panels', []):
    if panel.get('id') == 10:
        raw_sql = panel['targets'][0]['rawSql']
        print("FOUND PANEL 10 QUERY:")
        print(raw_sql[:500])
        print("...")
        print(raw_sql[-500:])
