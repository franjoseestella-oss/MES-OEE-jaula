import json
import urllib.request
import urllib.error
import base64
import os
import sys

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

uid = "mes-plan-v1"
filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

print(f"Checking UID: {uid} against {filepath}")
if not os.path.exists(filepath):
    print(f"Local file {filepath} does not exist!")
    sys.exit(1)

# Fetch live
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        existing = json.loads(resp.read().decode("utf-8"))
        live_dashboard = existing["dashboard"]
except urllib.error.HTTPError as e:
    print(f"Error fetching live dashboard: {e.code} - {e.read().decode()}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
    
with open(filepath, "r", encoding="utf-8") as f:
    local_dashboard = json.load(f)
    
# We want to compare the essential properties. Let's compare the serialized strings
# but ignoring volatile fields like 'version', 'id', 'iteration'
def sanitize(db):
    db_copy = json.loads(json.dumps(db))
    db_copy.pop("version", None)
    db_copy.pop("id", None)
    db_copy.pop("iteration", None)
    return db_copy

live_sanitized = sanitize(live_dashboard)
local_sanitized = sanitize(local_dashboard)

live_str = json.dumps(live_sanitized, sort_keys=True, indent=2)
local_str = json.dumps(local_sanitized, sort_keys=True, indent=2)

if live_str == local_str:
    print("MATCH!")
else:
    print("DIFFERENCE DETECTED!")
    # print size diff
    print(f"Live len: {len(live_str)}, Local len: {len(local_str)}")
    with open("scratch/plan_live_sanitized.json", "w", encoding="utf-8") as f:
        f.write(live_str)
    with open("scratch/plan_local_sanitized.json", "w", encoding="utf-8") as f:
        f.write(local_str)
    print("Saved sanitized copies to scratch/plan_live_sanitized.json and scratch/plan_local_sanitized.json")
