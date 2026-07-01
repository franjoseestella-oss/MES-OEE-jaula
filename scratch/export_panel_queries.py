import json
import os

os.makedirs('scratch/panel_queries', exist_ok=True)

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for panel in data.get('panels', []):
    pid = panel.get('id')
    for idx, target in enumerate(panel.get('targets', [])):
        if 'rawSql' in target:
            filename = f"scratch/panel_queries/panel_{pid}_target_{idx}.sql"
            with open(filename, 'w', encoding='utf-8') as sf:
                sf.write(target['rawSql'])
            print(f"Exported panel {pid} target {idx} to {filename}")
