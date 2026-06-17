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

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def push_dashboard(filepath, message):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        dashboard = json.load(f)
        
    # Remove version and ID before pushing to prevent version conflicts
    dashboard_to_push = dict(dashboard)
    dashboard_to_push.pop("id", None)
    dashboard_to_push["version"] = None
    
    # Dynamically find the folder ID for 'Logisnext MES'
    folder_id = 0
    try:
        req_folders = urllib.request.Request(f"{GRAFANA_URL}/api/folders", headers=headers)
        with urllib.request.urlopen(req_folders) as resp_folders:
            folders = json.loads(resp_folders.read().decode("utf-8"))
            for fld in folders:
                if fld.get("title") == "Logisnext MES":
                    folder_id = fld.get("id", 0)
                    break
    except Exception as e:
        safe_print(f"Error fetching folders: {e}")
    
    payload = {
        "dashboard": dashboard_to_push,
        "overwrite": True,
        "folderId": folder_id,
        "message": message
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=data, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            safe_print(f"Pushed {dashboard.get('title')} to Grafana. Status: {result.get('status')} | Version: {result.get('version')}")
            
            # Fetch the updated dashboard back to keep the file fully synced with ID and version
            uid = dashboard.get('uid')
            req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
            with urllib.request.urlopen(req_get) as resp_get:
                existing = json.loads(resp_get.read().decode("utf-8"))
                final_dashboard = existing["dashboard"]
                
            with open(filepath, "w", encoding="utf-8") as fw:
                json.dump(final_dashboard, fw, indent=2, ensure_ascii=False)
            safe_print(f"Synced back and updated {filepath}")
    except urllib.error.HTTPError as e:
        safe_print(f"HTTP Error {e.code} for {dashboard.get('title')}: {e.read().decode()}")

def main():
    dashboard_dir = 'grafana/provisioning/dashboards'
    files = [
        ('home_dashboard.json', 'Push INICIO dashboard'),
        ('distribuidor_dashboard.json', 'Push DISTRIBUIDOR dashboard'),
        ('alarmas_dashboard.json', 'Push ALARMAS dashboard'),
        ('registro_dashboard.json', 'Push REGISTRO dashboard'),
        ('plan_dashboard.json', 'Push PLAN dashboard with pacing queries'),
        ('turno_actual_dashboard.json', 'Push TURNO ACTUAL dashboard')
    ]
    for filename, msg in files:
        filepath = os.path.join(dashboard_dir, filename)
        if os.path.exists(filepath):
            push_dashboard(filepath, msg)

if __name__ == '__main__':
    main()
