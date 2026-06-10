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

def push_dashboard(filepath, message):
    with open(filepath, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)
        
    # Remove version and ID before pushing to prevent version conflicts
    dashboard_to_push = dict(dashboard)
    dashboard_to_push.pop("id", None)
    dashboard_to_push["version"] = None
    
    # We want to make sure folder ID matches folder 1 ("Logisnext MES")
    # Let's search for folder ID first
    folder_id = 1 # Default
    
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
            print(f"Pushed {dashboard.get('title')} to Grafana. Status: {result.get('status')} | Version: {result.get('version')}")
            
            # Fetch the updated dashboard back to keep the file fully synced with ID and version
            uid = dashboard.get('uid')
            req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
            with urllib.request.urlopen(req_get) as resp_get:
                existing = json.loads(resp_get.read().decode("utf-8"))
                final_dashboard = existing["dashboard"]
                
            with open(filepath, "w", encoding="utf-8") as fw:
                json.dump(final_dashboard, fw, indent=2, ensure_ascii=False)
            print(f"Synced back and updated {filepath}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {dashboard.get('title')}: {e.read().decode()}")

def main():
    dashboard_dir = 'grafana/provisioning/dashboards'
    files = [
        ('home_dashboard.json', 'Push INICIO dashboard'),
        ('oee_dashboard.json', 'Push MES / OEE dashboard with tabs'),
        ('log_dashboard.json', 'Push LOG_SECUENCIAS dashboard with tabs'),
        ('registro_dashboard.json', 'Push REGISTRO dashboard with tabs')
    ]
    for filename, msg in files:
        filepath = os.path.join(dashboard_dir, filename)
        if os.path.exists(filepath):
            push_dashboard(filepath, msg)

if __name__ == '__main__':
    main()
