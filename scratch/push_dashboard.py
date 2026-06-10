import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Read local log_dashboard.json
with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

# Strip id to avoid conflict, set overwrite
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Split detailed tests table into OK and NOK tables"
}

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/db", data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print("Success! Status:", result.get("status"))
        print("URL:", result.get("url"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode("utf-8"))
