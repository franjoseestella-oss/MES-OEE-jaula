import json
import requests

dashboard_path = "scratch/plan_dashboard_8am.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

# Strip id to let Grafana match by UID and avoid conflict if ID has shifted
if "id" in dashboard_data:
    del dashboard_data["id"]

payload = {
    "dashboard": dashboard_data,
    "folderUid": "dfovv23tkq48wc",
    "overwrite": True
}

auth = ("fran.jose.estella@gmail.com", "admin123")
url = "http://localhost:3010/api/dashboards/db"

headers = {
    "Content-Type": "application/json"
}

res = requests.post(url, json=payload, auth=auth, headers=headers)
print(f"Status Code: {res.status_code}")
print(f"Response: {res.text}")
