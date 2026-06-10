import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# 1. Fetch current dashboard
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")

# 2. Modify Panel 14
panel_14 = None
for p in dashboard["panels"]:
    if p.get("id") == 14:
        panel_14 = p
        break

if panel_14:
    panel_14["options"]["displayMode"] = "gradient"
    panel_14["options"]["showThresholdLabels"] = True
    panel_14["options"]["showThresholdMarkers"] = True
    print("Updated Panel 14 options: displayMode=gradient, showThresholdLabels=True, showThresholdMarkers=True")

# 3. Push back
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Test enabling threshold labels on Panel 14"
}
if folder_uid:
    payload["folderUid"] = folder_uid

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/db", data=data, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode("utf-8"))
    print("Success! Status:", result.get("status"))
