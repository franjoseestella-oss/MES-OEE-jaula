import json
import urllib.request
import urllib.error
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL = "http://localhost:3010"
GRAFANA_USER = "fran.jose.estella@gmail.com"
GRAFANA_PASS = "admin123"
PROV_FILE = "grafana/provisioning/dashboards/oee_dashboard.json"
FOLDER_UID = "dfolgqxjcao00d"

print(f"Reading local dashboard from {PROV_FILE}...")
with open(PROV_FILE, 'r', encoding='utf-8') as f:
    local_dash = json.load(f)

# Ensure the UID is set correctly
local_dash["uid"] = "mes-oee-v1"

payload = {
    "dashboard": local_dash,
    "folderUid": FOLDER_UID,
    "overwrite": True,
    "message": "fix: update panel threshold mappings for double dynamic thresholds"
}

creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Content-Type": "application/json"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data,
    headers=headers,
    method='POST'
)

print("Deploying dashboard to Grafana...")
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"Success! Status: {result.get('status')}, Version: {result.get('version')}, URL: {result.get('url')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8', errors='replace')}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
