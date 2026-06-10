import json

with open('grafana/provisioning/dashboards/log_dashboard.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

for p in d.get('panels', []):
    if p.get('id') == 9:
        print("SQL Target Query:")
        for t in p.get('targets', []):
            print(t.get('rawSql'))
        print("\nField Configurations/Overrides:")
        print(json.dumps(p.get('fieldConfig', {}).get('overrides', []), indent=2))
