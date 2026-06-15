"""
Restore fixed min/max scale on the 4 individual gauge panels (16,17,18,19).
Sin carga: min=1, max=6
Con carga: min=1, max=8
Dynamic thresholds (green/red) still come from configFromData, but the arc
scale is fixed so you always see the full 1-6 range.
"""
import json, urllib.request, urllib.error, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL   = "http://localhost:3010"
GRAFANA_USER  = "fran.jose.estella@gmail.com"
GRAFANA_PASS  = "admin123"
DASHBOARD_UID = "mes-oee-v1"

creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}", headers=headers)
with urllib.request.urlopen(req) as r:
    live = json.loads(r.read())

dash = live["dashboard"]
folder_id = live.get("meta", {}).get("folderId", 0)

# Panel IDs -> (min, max)
# 16 = Elevacion Sin Carga, 17 = Descenso Sin Carga -> 1 a 6
# 18 = Elevacion Con Carga, 19 = Descenso Con Carga -> 1 a 8
scale_map = {16: (1, 6), 17: (1, 6), 18: (1, 8), 19: (1, 8)}

for p in dash["panels"]:
    pid = p["id"]
    if pid in scale_map:
        mn, mx = scale_map[pid]
        p["fieldConfig"]["defaults"]["min"] = mn
        p["fieldConfig"]["defaults"]["max"] = mx
        print(f"Panel {pid} ({p['title']}): min={mn}, max={mx}")

payload = json.dumps({
    "dashboard": dash,
    "folderId": folder_id,
    "overwrite": True,
    "message": "fix: restore fixed scale min/max on individual gauge panels"
}).encode("utf-8")

req2 = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=payload, headers=headers, method="POST"
)
with urllib.request.urlopen(req2) as r:
    result = json.loads(r.read())
    print(f"Dashboard OK: {result.get('status')}, version {result.get('version')}")

# Update provisioning JSON
prov = "grafana/provisioning/dashboards/oee_dashboard.json"
with open(prov, "r", encoding="utf-8") as f:
    local = json.load(f)

for p in local["panels"]:
    pid = p["id"]
    if pid in scale_map:
        mn, mx = scale_map[pid]
        p["fieldConfig"]["defaults"]["min"] = mn
        p["fieldConfig"]["defaults"]["max"] = mx

with open(prov, "w", encoding="utf-8") as f:
    json.dump(local, f, indent=2, ensure_ascii=False)
print(f"Updated {prov}")
