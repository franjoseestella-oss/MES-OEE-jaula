import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

# Find panel 10
found = False
for p in dashboard_data.get("panels", []):
    if p.get("id") == 10:
        found = True
        print("Found panel 10.")
        
        # We want to have partitionByValues AND renameByRegex
        p["transformations"] = [
            {
                "id": "partitionByValues",
                "options": {
                    "fields": ["metric"]
                }
            },
            {
                "id": "renameByRegex",
                "options": {
                    "regex": "^value\\s(.+)",
                    "renamePattern": "$1"
                }
            }
        ]
        print("Set transformations: partitionByValues and renameByRegex")
        break

if not found:
    print("Panel 10 not found in local dashboard!")
    sys.exit(1)

# Write back to disk
with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
print("Saved plan_dashboard.json to disk.")

# Push to Grafana
if "id" in dashboard_data:
    del dashboard_data["id"]

payload = {
    "dashboard": dashboard_data,
    "folderUid": "dfovv23tkq48wc",
    "overwrite": True,
    "message": "fix: clean up panel 10 Y-axis labels by removing 'value' prefix via renameByRegex"
}

auth = ("fran.jose.estella@gmail.com", "admin123")
url = "http://localhost:3010/api/dashboards/db"
headers = {"Content-Type": "application/json"}

res = requests.post(url, json=payload, auth=auth, headers=headers)
print(f"Grafana API Response status: {res.status_code}")
print(f"Response text: {res.text}")
