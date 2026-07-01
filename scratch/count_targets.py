import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    pid = p.get('id')
    if pid in [4, 5, 10]:
        print(f"Panel {pid} ({p.get('title')}):")
        targets = p.get('targets', [])
        print(f"  Number of targets: {len(targets)}")
        for i, t in enumerate(targets):
            sql = t.get('rawSql', '')
            print(f"    Target {i}: refId={t.get('refId')}, rawSql length={len(sql)}")
