import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
filepath = 'scratch/backup_dashboards/oee_dashboard.json'

with open(filepath, 'r', encoding='utf-8') as f:
    db = json.load(f)
    print('Title:', db.get('title'))
    print('UID:', db.get('uid'))
    print('Number of panels:', len(db.get('panels', [])))
    for i, p in enumerate(db.get('panels', [])):
        print(f"Panel {i}: {p.get('title')} ({p.get('type')})")
