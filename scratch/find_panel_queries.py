import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for panel in data.get('panels', []):
    title = panel.get('title', '').encode('ascii', 'replace').decode('ascii')
    ptype = panel.get('type', '')
    print(f"Panel ID: {panel.get('id')}, Title: {title}, Type: {ptype}")
    for target in panel.get('targets', []):
        if 'rawSql' in target:
            q_preview = target['rawSql'][:100].strip().replace('\n', ' ').replace('\r', '')
            q_preview = q_preview.encode('ascii', 'replace').decode('ascii')
            print(f"  Query: {q_preview}...")
