import json
import urllib.request
import urllib.error
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

mapping = {
    "mes-home-v1": "grafana/provisioning/dashboards/home_dashboard.json",
    "mes-alarms-v1": "grafana/provisioning/dashboards/alarmas_dashboard.json",
    "mes-reg-v1": "grafana/provisioning/dashboards/registro_dashboard.json",
    "mes-oee-v2": "grafana/provisioning/dashboards/distribuidor_dashboard.json",
    "mes-plan-v1": "grafana/provisioning/dashboards/plan_dashboard.json",
    "panel-oee-mes-fabrica": "grafana/provisioning/dashboards/turno_actual_dashboard.json"
}

def download_dashboard(uid, filepath):
    url = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"
    print(f"Downloading dashboard UID '{uid}' -> '{filepath}'...")
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            db_model = data.get("dashboard")
            if db_model:
                # Save to file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(db_model, f, indent=2, ensure_ascii=False)
                print(f"Successfully saved {filepath}!")
            else:
                print(f"Error: No dashboard model found in response for UID '{uid}'")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error downloading {uid}: {e}")

for uid, filepath in mapping.items():
    download_dashboard(uid, filepath)
