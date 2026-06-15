import json
import sys

def main():
    with open('grafana/provisioning/dashboards/distribuidor_dashboard.json', encoding='utf-8') as f:
        d = json.load(f)
    
    p_ids = [10, 11, 16, 17, 18, 19]
    for p in d.get('panels', []):
        pid = p.get('id')
        if pid in p_ids or p.get('type') == 'row':
            print(f"=== Panel ID {pid}: {p.get('title')} ({p.get('type')}) ===")
            sub = {k: v for k, v in p.items() if k in ('targets', 'transformations', 'fieldConfig', 'options')}
            print(json.dumps(sub, indent=2))
            print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    main()
