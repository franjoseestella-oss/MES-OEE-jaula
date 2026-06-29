import json
import sys

# force utf-8 output
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"grafana/provisioning/dashboards/plan_dashboard.json"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    with open(file_path, "r", encoding="utf-16") as f:
        data = json.load(f)

print(f"Dashboard Title: {data.get('title')}")
print(f"UID: {data.get('uid')}")
print(f"Version: {data.get('version')}")

panels = data.get("panels", [])
print(f"Number of panels: {len(panels)}")
for p in panels:
    print(f"ID: {p.get('id')}, Title: '{p.get('title')}', Type: '{p.get('type')}'")
