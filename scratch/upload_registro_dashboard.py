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

file_path = "grafana/provisioning/dashboards/registro_dashboard.json"
with open(file_path, 'r', encoding='utf-8') as f:
    dashboard_data = json.load(f)

payload = {
    "dashboard": dashboard_data,
    "overwrite": True,
    "message": "Move OK_NOK next to NBASTIDOR in the three tables"
}

req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=json.dumps(payload).encode('utf-8'),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Successfully updated dashboard in Grafana:")
        print(json.dumps(res, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
