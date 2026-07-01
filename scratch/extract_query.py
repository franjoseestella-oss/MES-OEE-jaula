import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    if p.get('id') == 10:
        for target in p.get('targets', []):
            if 'rawSql' in target:
                with open('scratch/query_panel10.sql', 'w', encoding='utf-8') as out:
                    out.write(target['rawSql'])
                print("Query saved to scratch/query_panel10.sql")
