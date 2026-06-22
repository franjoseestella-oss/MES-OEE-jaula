import json
import requests

url = "http://localhost:3010/api/dashboards/db"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
auth = ("fran.jose.estella@gmail.com", "admin123")

# Load dashboard
with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dashboard_model = json.load(f)

# Ensure correct properties for API save
payload = {
    "dashboard": dashboard_model,
    "overwrite": True,
    "message": "Shifted queries to use plot date for timeline visualization"
}

resp = requests.post(url, json=payload, headers=headers, auth=auth)
print(f"Status Code: {resp.status_code}")
print(f"Response: {resp.text}")
