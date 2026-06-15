"""
Deploy the patched JS to Grafana container + update dashboard:
1. Copy patched JS to container
2. Restart Grafana to reload manifest
3. Update dashboard panels to enable showThresholdMarkers and add threshold2 mappings
"""
import sys, json, subprocess, urllib.request, urllib.error, base64
sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL  = "http://localhost:3010"
GRAFANA_USER = "fran.jose.estella@gmail.com"
GRAFANA_PASS = "admin123"
DASHBOARD_UID = "mes-oee-v1"
CONTAINER = "mes_grafana"
JS_FILE = "scratch/5017.aaaa340b86e350c74a1f.js"
CONTAINER_PATH = "/usr/share/grafana/public/build/5017.aaaa340b86e350c74a1f.js"

# ─── Step 1: Copy patched JS to container ────────────────────────────────────
print("Step 1: Copying patched JS to container...")
r = subprocess.run(
    ['docker', 'cp', JS_FILE, f'{CONTAINER}:{CONTAINER_PATH}'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if r.returncode != 0:
    print(f"ERROR copying JS: {r.stderr}")
    sys.exit(1)
print("  ✓ JS copied")

# ─── Step 2: Restart Grafana to reload manifest from disk ────────────────────
print("Step 2: Restarting Grafana container...")
r2 = subprocess.run(
    ['docker', 'restart', CONTAINER],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if r2.returncode != 0:
    print(f"ERROR restarting: {r2.stderr}")
    sys.exit(1)
print("  ✓ Grafana restarting...")

# Wait for Grafana to be ready
import time
for attempt in range(20):
    time.sleep(2)
    try:
        r3 = urllib.request.urlopen(f"{GRAFANA_URL}/api/health", timeout=3)
        data = json.loads(r3.read())
        if data.get('database') == 'ok':
            print(f"  ✓ Grafana ready (attempt {attempt+1})")
            break
    except:
        pass
else:
    print("  WARNING: Grafana not responding after 40s, continuing anyway...")

# ─── Step 3: Update dashboard via API ────────────────────────────────────────
print("\nStep 3: Updating dashboard panels...")

creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

# Get current live dashboard
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}", headers=headers
)
with urllib.request.urlopen(req) as resp:
    live = json.loads(resp.read())

live_dash = live['dashboard']
folder_id = live.get('meta', {}).get('folderId', 0)

# ─── Fix panels 14 (bargauge) and 15 (gauge) ─────────────────────────────────
# For each configFromData transformation:
#   - Add threshold2 mapping if missing
#   - Enable showThresholdMarkers and showThresholdLabels on gauge

GAUGE_FIELDS = [
    "Elevacion Sin Carga",
    "Descenso Sin Carga",
    "Elevacion Con Carga",
    "Descenso Con Carga",
]

def fix_configfromdata_transforms(panel):
    """Ensure each configFromData transform has both threshold1 and threshold2 mappings."""
    transforms = panel.get('transformations', [])
    for tr in transforms:
        if tr.get('id') != 'configFromData':
            continue
        opts = tr.get('options', {})
        apply_to_field = opts.get('applyTo', {}).get('options', '')
        if apply_to_field not in GAUGE_FIELDS:
            continue

        mappings = opts.get('mappings', [])
        has_th2 = any(m.get('handlerKey') == 'threshold2' for m in mappings)

        # Find the Min field name (used for threshold1)
        th1_field = next((m['fieldName'] for m in mappings if m.get('handlerKey') == 'threshold1'), None)

        if not has_th2 and th1_field:
            # Derive Max field name from Min field name
            max_field = th1_field.replace(' Min', ' Max')
            mappings.append({
                "fieldName": max_field,
                "handlerArguments": {"threshold": {"color": "#E32636"}},
                "handlerKey": "threshold2"
            })
            print(f"  ✓ Added threshold2 mapping: '{max_field}' → threshold2 for '{apply_to_field}'")
        elif has_th2:
            print(f"  - threshold2 already exists for '{apply_to_field}'")

        opts['mappings'] = mappings

    return panel


def fix_panel_display(panel):
    """Enable threshold markers/labels on gauge and bargauge panels."""
    opts = panel.get('options', {})
    ptype = panel.get('type', '')

    if ptype == 'gauge':
        changed = []
        if not opts.get('showThresholdMarkers', True):
            opts['showThresholdMarkers'] = True
            changed.append('showThresholdMarkers=True')
        if not opts.get('showThresholdLabels', False):
            opts['showThresholdLabels'] = True
            changed.append('showThresholdLabels=True')
        # Remove fixed min/max so dynamic values from threshold handlers take over
        fc = panel.get('fieldConfig', {}).get('defaults', {})
        if 'min' in fc:
            del fc['min']
            changed.append('removed fixed min')
        if 'max' in fc:
            del fc['max']
            changed.append('removed fixed max')
        if changed:
            print(f"  ✓ Panel {panel['id']} gauge: {', '.join(changed)}")

    elif ptype == 'bargauge':
        if opts.get('displayMode') != 'basic':
            opts['displayMode'] = 'basic'
            print(f"  ✓ Panel {panel['id']} bargauge: displayMode=basic")
        # Remove fixed min/max from bargauge fieldConfig too
        fc = panel.get('fieldConfig', {}).get('defaults', {})
        if 'min' in fc and panel['id'] == 14:
            del fc['min']
            print(f"  ✓ Panel {panel['id']} bargauge: removed fixed min")
        if 'max' in fc and panel['id'] == 14:
            del fc['max']
            print(f"  ✓ Panel {panel['id']} bargauge: removed fixed max")

    return panel


# Process panels
for p in live_dash.get('panels', []):
    pid = p['id']
    ptype = p.get('type', '')
    if ptype in ('gauge', 'bargauge') and pid in (14, 15):
        fix_configfromdata_transforms(p)
        fix_panel_display(p)

# ─── Push updated dashboard ───────────────────────────────────────────────────
payload = json.dumps({
    "dashboard": live_dash,
    "folderId": folder_id,
    "overwrite": True,
    "message": "fix: threshold2 handler + dynamic min/max scale + threshold markers"
}).encode('utf-8')

req2 = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=payload, headers=headers, method='POST'
)
try:
    with urllib.request.urlopen(req2) as resp:
        result = json.loads(resp.read())
        print(f"\n✓ Dashboard pushed: status={result.get('status')}, version={result.get('version')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)

# ─── Also update the provisioning JSON file ───────────────────────────────────
print("\nStep 4: Updating local provisioning JSON...")
prov_file = "grafana/provisioning/dashboards/oee_dashboard.json"
with open(prov_file, 'r', encoding='utf-8') as f:
    local_dash = json.load(f)

for p in local_dash.get('panels', []):
    pid = p['id']
    ptype = p.get('type', '')
    if ptype in ('gauge', 'bargauge') and pid in (14, 15):
        fix_configfromdata_transforms(p)
        fix_panel_display(p)

with open(prov_file, 'w', encoding='utf-8') as f:
    json.dump(local_dash, f, indent=2, ensure_ascii=False)
print(f"  ✓ Saved {prov_file}")

print("\n=== DONE ===")
print("Hard-refresh the browser (Ctrl+Shift+R) to load the new JS bundle.")
