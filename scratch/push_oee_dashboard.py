import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# 1. Load the local oee_dashboard.json
filepath = 'grafana/provisioning/dashboards/oee_dashboard.json'
with open(filepath, 'r', encoding='utf-8') as f:
    dashboard = json.load(f)

# Get existing version from Grafana to check/increment
try:
    req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-oee-v1", headers=headers)
    with urllib.request.urlopen(req_get) as resp_get:
        existing = json.loads(resp_get.read().decode("utf-8"))
        folder_uid = existing["meta"].get("folderUid", "")
        # Increment version to make sure it updates
        current_version = existing["dashboard"].get("version", 1)
        dashboard["version"] = current_version + 1
        print(f"Current Grafana dashboard version: {current_version}. Pushing version: {dashboard['version']}")
except Exception as e:
    print("Could not fetch existing version (might not exist yet):", e)
    folder_uid = ""
    dashboard["version"] = 1

# Remove ID for overwrite
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Update dynamic threshold colors for panel 14 and 15"
}
if folder_uid:
    payload["folderUid"] = folder_uid

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data, headers=headers, method="POST"
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"Dashboard pushed successfully. Status: {result.get('status')}")
        
        # Save the updated dashboard with ID/version back to local file
        new_uid = result.get('uid')
        req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{new_uid}", headers=headers)
        with urllib.request.urlopen(req_get) as resp_get:
            existing = json.loads(resp_get.read().decode("utf-8"))
            final_dashboard = existing["dashboard"]
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(final_dashboard, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved updated dashboard back to {filepath}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print("Error:", e)
