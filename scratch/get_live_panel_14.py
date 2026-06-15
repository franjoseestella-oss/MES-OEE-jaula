import urllib.request, json, base64

GRAFANA_URL  = "http://localhost:3010"
GRAFANA_USER = "fran.jose.estella@gmail.com"
GRAFANA_PASS = "admin123"
DASHBOARD_UID = "mes-oee-v1"

creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}", headers=headers)
with urllib.request.urlopen(req) as resp:
    live = json.loads(resp.read())

p14 = next(p for p in live['dashboard']['panels'] if p['id'] == 14)
print(json.dumps(p14, indent=2))
