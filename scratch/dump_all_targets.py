import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    pid = p.get('id')
    if pid in [4, 5, 10]:
        print(f"\n==================== PANEL {pid}: {p.get('title')} ====================")
        for i, t in enumerate(p.get('targets', [])):
            print(f"--- Target {i} (refId={t.get('refId')}) ---")
            print(t.get('rawSql'))
