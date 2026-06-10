import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Fetch current dashboard from live Grafana
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        existing = json.loads(resp.read().decode("utf-8"))
        
    dashboard = existing["dashboard"]
    
    # Save to the provisioning path
    target_path = "grafana/provisioning/dashboards/log_dashboard.json"
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved live dashboard to {target_path}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
