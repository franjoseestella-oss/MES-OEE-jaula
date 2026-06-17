import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-oee-v2", headers=headers)
try:
    print("Fetching live mes-oee-v2 dashboard...")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        live_dashboard = data["dashboard"]
        
    target_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
    print(f"Saving to {target_path}...")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(live_dashboard, f, indent=2, ensure_ascii=False)
    print("Done!")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
