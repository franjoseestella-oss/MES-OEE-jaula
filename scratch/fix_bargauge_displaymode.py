"""Fix bargauge displayMode from 'gradient' to 'basic' in oee_dashboard.json
and push the result to Grafana via API."""
import json, sys, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL = "http://localhost:3010"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"
DASHBOARD_FILE = "grafana/provisioning/dashboards/oee_dashboard.json"
DASHBOARD_UID = "mes-oee-v1"

# --- Read local JSON ---
with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
    dash = json.load(f)

# --- Patch bar gauge panels ---
changed = []
for p in dash.get('panels', []):
    if p.get('type') == 'bargauge':
        opts = p.get('options', {})
        old_mode = opts.get('displayMode', '')
        if old_mode != 'basic':
            opts['displayMode'] = 'basic'
            changed.append(f"Panel {p['id']} '{p.get('title','')}': {old_mode} → basic")

print("Changed panels:")
for c in changed:
    print(" ", c)

# --- Save local JSON ---
with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
    json.dump(dash, f, indent=2, ensure_ascii=False)
print(f"Saved {DASHBOARD_FILE}")

# --- Push to Grafana API ---
import base64
creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {creds}"
}

# Get current dashboard from Grafana to get correct version
url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    live = json.loads(resp.read())

live_dash = live['dashboard']
live_dash_version = live_dash.get('version', 0)
folder_id = live.get('meta', {}).get('folderId', 0)

# Update panels in the live dashboard
for p in live_dash.get('panels', []):
    if p.get('type') == 'bargauge':
        p.get('options', {})['displayMode'] = 'basic'

payload = json.dumps({
    "dashboard": live_dash,
    "folderId": folder_id,
    "overwrite": True,
    "message": "fix: bargauge displayMode basic (no gradient)"
}).encode('utf-8')

req2 = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=payload,
    headers=headers,
    method='POST'
)
try:
    with urllib.request.urlopen(req2) as resp:
        result = json.loads(resp.read())
        print("Grafana API response:", result.get('status'), result.get('version'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
