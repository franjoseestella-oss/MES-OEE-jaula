import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"
TARGET_PATH = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\log_dashboard.json"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# Fetch the live dashboard definition
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode("utf-8"))

dashboard = result["dashboard"]

# Normalize/clean up database-specific/volatile properties if any, but preserve version/schema
# Usually provisioned dashboards should have clean JSON.
# We write the entire dashboard JSON to the provisioning path
with open(TARGET_PATH, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f"Successfully saved live dashboard to {TARGET_PATH}")
