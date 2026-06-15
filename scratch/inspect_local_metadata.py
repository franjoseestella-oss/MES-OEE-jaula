import json

files = [
    "grafana/provisioning/dashboards/alarmas_dashboard.json",
    "grafana/provisioning/dashboards/home_dashboard.json",
    "grafana/provisioning/dashboards/oee_dashboard.json",
    "grafana/provisioning/dashboards/registro_dashboard.json"
]

for fpath in files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            db = json.load(f)
            print(f"{fpath}:")
            print(f"  id: {db.get('id')}")
            print(f"  uid: {db.get('uid')}")
            print(f"  version: {db.get('version')}")
            print(f"  panels count: {len(db.get('panels', []))}")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
