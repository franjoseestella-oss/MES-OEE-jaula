import json
import urllib.request
import urllib.error
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

# 1. First make a backup of the current local dashboards
backup_dir = "scratch/backup_dashboards"
os.makedirs(backup_dir, exist_ok=True)
print("Backing up current local dashboards...")
for uid, filepath in mappings.items():
    if os.path.exists(filepath):
        backup_path = os.path.join(backup_dir, os.path.basename(filepath))
        with open(filepath, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        print(f"  Backed up {filepath} -> {backup_path}")

# 2. Fetch live dashboards and overwrite local files
print("\nFetching live dashboards from Grafana and saving them...")
for uid, filepath in mappings.items():
    req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            live_dashboard = data["dashboard"]
            
            # Save to provisioning file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(live_dashboard, f, indent=2, ensure_ascii=False)
            print(f"  Successfully saved live {uid} to {filepath}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error fetching {uid}: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"  Error fetching {uid}: {e}")

print("\nAll live dashboards processed.")
