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
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
panel_15 = next((p for p in dashboard["panels"] if p.get("id") == 15), None)

if panel_15:
    print(json.dumps(panel_15, indent=2, ensure_ascii=False))
else:
    print("Panel 15 not found")
