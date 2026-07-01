import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    pid = p.get('id')
    if pid in [4, 5, 10]:
        title = p.get('title', f'panel_{pid}').replace(' ', '_').replace('(', '').replace(')', '').replace('📅', '').strip()
        for i, t in enumerate(p.get('targets', [])):
            refId = t.get('refId', f'target_{i}')
            filename = f"scratch/panel_{pid}_{refId}_{title}.sql"
            raw_sql = t.get('rawSql', '')
            with open(filename, 'w', encoding='utf-8') as out_f:
                out_f.write(raw_sql)
            print(f"Saved query for Panel {pid} (Target {refId}) to {filename}")
