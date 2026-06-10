import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"
DASHBOARD_FILE = r"grafana\provisioning\dashboards\log_dashboard.json"

# Read local dashboard JSON
with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

# Get current dashboard to find the folderId
auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json",
}

req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/{dashboard['uid']}",
    headers=headers,
)
try:
    with urllib.request.urlopen(req) as resp:
        existing = json.loads(resp.read().decode("utf-8"))
        folder_id = existing["meta"]["folderId"]
        print(f"Existing dashboard found. Folder ID: {folder_id}, Version: {existing['dashboard'].get('version')}")
except urllib.error.HTTPError as e:
    print(f"Dashboard not found: {e.code}")
    folder_id = 0

# Set version to None and overwrite to True
dashboard["version"] = None
dashboard.pop("id", None)

payload = {
    "dashboard": dashboard,
    "folderId": folder_id,
    "overwrite": True,
    "message": "Pushed debug version"
}

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data,
    headers=headers,
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print("Push Result:", json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
