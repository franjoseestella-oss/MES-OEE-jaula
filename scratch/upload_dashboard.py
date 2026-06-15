import os
import json
import requests

url = "http://localhost:3010/api/dashboards/db"
token = os.environ.get("GRAFANA_TOKEN", "")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

# The root elements under "dashboard" should not contain "id" if we want to overwrite/re-create or update it dynamically
# but since mes-plan-v1 is already created, having id=14 or matching uid is fine. Let's send the correct payload structure.
payload = {
    "dashboard": dashboard_data,
    "folderUid": "dfovv23tkq48wc",
    "overwrite": True
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status Code: {response.status_code}")
print("Response text:", response.text)
