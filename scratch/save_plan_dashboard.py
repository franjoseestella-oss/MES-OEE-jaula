import json
import requests

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"
grafana_url = "http://localhost:3010/api/dashboards/db"
auth = ("fran.jose.estella@gmail.com", "admin123")

print("Loading local plan_dashboard.json...")
with open(dashboard_path, "r", encoding="utf-8-sig") as f:
    dashboard_data = json.load(f)

# Ensure the style is set to dark
dashboard_data["style"] = "dark"

payload = {
    "dashboard": dashboard_data,
    "overwrite": True,
    "folderUid": "dfovv23tkq48wc"
}

print(f"Sending POST request to {grafana_url}...")
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(grafana_url, json=payload, auth=auth, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"An error occurred: {e}")
