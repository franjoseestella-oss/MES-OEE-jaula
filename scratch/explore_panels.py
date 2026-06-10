import json
import os

filepath = r'grafana/provisioning/dashboards/log_dashboard.json'
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        d = json.load(f)
    for p in d.get('panels', []):
        safe_title = p.get('title', '').encode('ascii', 'replace').decode('ascii')
        print(f"Panel ID {p.get('id')}: Type: {p.get('type')}, Grid: {p.get('gridPos')}, Title: {safe_title}")
else:
    print("File not found")
