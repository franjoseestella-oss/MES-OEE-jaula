import json
import glob

files = glob.glob("grafana/provisioning/dashboards/*.json")
for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"{filepath}: {data.get('timezone')}")
