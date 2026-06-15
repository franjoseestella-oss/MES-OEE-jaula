import json
import urllib.request
import urllib.error
import base64
import os

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

mappings = {
    "mes-alarms-v1": "grafana/provisioning/dashboards/alarmas_dashboard.json",
    "mes-home-v1": "grafana/provisioning/dashboards/home_dashboard.json",
    "mes-oee-v1": "grafana/provisioning/dashboards/oee_dashboard.json",
    "mes-reg-v1": "grafana/provisioning/dashboards/registro_dashboard.json"
}

for uid, filepath in mappings.items():
    print(f"\n--- Checking UID: {uid} against {filepath} ---")
    if not os.path.exists(filepath):
        print(f"Local file {filepath} does not exist!")
        continue
    
    # Fetch live
    req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            existing = json.loads(resp.read().decode("utf-8"))
            live_dashboard = existing["dashboard"]
    except urllib.error.HTTPError as e:
        print(f"Error fetching live dashboard: {e.code} - {e.read().decode()}")
        continue
    except Exception as e:
        print(f"Error: {e}")
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        local_dashboard = json.load(f)
        
    # We want to compare the essential properties. Let's compare the serialized strings
    # but ignoring volatile fields like 'version', 'id', 'iteration'
    def sanitize(db):
        db_copy = json.loads(json.dumps(db))
        db_copy.pop("version", None)
        db_copy.pop("id", None)
        db_copy.pop("iteration", None)
        # also sanitize panels volatile fields if any
        for panel in db_copy.get("panels", []):
            panel.pop("version", None)
            panel.pop("id", None)  # wait, panel ids might be important, but maybe not volatile
        return db_copy

    live_sanitized = sanitize(live_dashboard)
    local_sanitized = sanitize(local_dashboard)
    
    live_str = json.dumps(live_sanitized, sort_keys=True, indent=2)
    local_str = json.dumps(local_sanitized, sort_keys=True, indent=2)
    
    if live_str == local_str:
        print("MATCH!")
    else:
        print("DIFFERENCE DETECTED!")
        # Let's save a temp file to see the differences
        os.makedirs("scratch/diff", exist_ok=True)
        with open(f"scratch/diff/{uid}_live.json", "w", encoding="utf-8") as f:
            f.write(live_str)
        with open(f"scratch/diff/{uid}_local.json", "w", encoding="utf-8") as f:
            f.write(local_str)
        print(f"Saved live and local copies to scratch/diff/ for comparison.")
