import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

for p in d.get('panels', []):
    if p.get('id') == 15:
        print("SQL Target Query:")
        for t in p.get('targets', []):
            print(t.get('rawSql'))
        print("\nPanel definition:")
        # print first 50 lines of formatted json of panel 15
        lines = json.dumps(p, indent=2).split('\n')
        print('\n'.join(lines[:120]))
