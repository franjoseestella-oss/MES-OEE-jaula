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

def upload_dashboard(filepath):
    print(f"Uploading {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        db_model = json.load(f)
    
    # Wrap in the structure Grafana expects
    payload = {
        "dashboard": db_model,
        "overwrite": True,
        "folderUid": "dfovv23tkq48wc" # Logisnext MES folder UID
    }
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"Successfully uploaded {filepath}! Status: {res.get('status')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error uploading {filepath}: {e}")

upload_dashboard("grafana/provisioning/dashboards/distribuidor_dashboard.json")
upload_dashboard("grafana/provisioning/dashboards/plan_dashboard.json")
