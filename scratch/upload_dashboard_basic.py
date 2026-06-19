import json
import requests

url = "http://localhost:3010/api/dashboards/db"
auth = ("fran.jose.estella@gmail.com", "admin123")
headers = {
    "Content-Type": "application/json"
}

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

payload = {
    "dashboard": dashboard_data,
    "folderUid": "dfovv23tkq48wc",
    "overwrite": True
}

try:
    response = requests.post(url, headers=headers, json=payload, auth=auth)
    print(f"Status Code: {response.status_code}")
    print("Response text:", response.text)
except Exception as e:
    print("Error:", e)
