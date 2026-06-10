import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    dashboard_data = json.loads(resp.read().decode("utf-8"))

dashboard = dashboard_data["dashboard"]
for panel in dashboard.get("panels", []):
    if panel.get("id") in [14, 15]:
        print(f"--- Panel ID: {panel['id']} | Title: {panel.get('title')} ---")
        print("fieldConfig defaults:")
        print(json.dumps(panel.get("fieldConfig", {}).get("defaults", {}), indent=2))
        print("transformations:")
        print(json.dumps(panel.get("transformations", []), indent=2))
