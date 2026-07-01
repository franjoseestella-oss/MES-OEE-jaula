import json

with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('panels', []):
    targets_str = str(p.get('targets', []))
    if 'LOG_ALARMAS' in targets_str or 'AlarmBase' in targets_str:
        print(f"Panel Title: {p.get('title')}")
        print(f"Panel ID: {p.get('id')}")
        for target in p.get('targets', []):
            if 'rawSql' in target:
                print("--- SQL ---")
                print(target['rawSql'])
                print("-----------")
