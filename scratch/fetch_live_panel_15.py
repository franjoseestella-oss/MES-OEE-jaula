import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json",
}

req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1",
    headers=headers,
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    dashboard = data["dashboard"]
    for panel in dashboard.get("panels", []):
        if panel.get("id") == 15:
            print(json.dumps(panel, indent=2))
