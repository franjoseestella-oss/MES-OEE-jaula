"""
Split panel 15 (4 gauges in one panel) into 4 SEPARATE gauge panels.
Each panel has its OWN SQL query returning only its metric + Min + Max.
This allows each gauge to have its own independent dynamic min/max scale.

Layout: same grid area as panel 15 (x:12, y:8, w:12, h:17)
Split into 2x2 grid: each panel w:6, h:8 (plus 1 row spacing)
"""
import json, sys, copy, urllib.request, urllib.error, base64
sys.stdout.reconfigure(encoding='utf-8')

GRAFANA_URL   = "http://localhost:3010"
GRAFANA_USER  = "fran.jose.estella@gmail.com"
GRAFANA_PASS  = "admin123"
DASHBOARD_UID = "mes-oee-v1"

creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

# ─── Get live dashboard ───────────────────────────────────────────────────────
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}", headers=headers)
with urllib.request.urlopen(req) as r:
    live = json.loads(r.read())

dash = live['dashboard']
folder_id = live.get('meta', {}).get('folderId', 0)

# ─── Read panel 15 as template ───────────────────────────────────────────────
panel15 = next((p for p in dash['panels'] if p['id'] == 15), None)
if not panel15:
    print("ERROR: Panel 15 not found!")
    sys.exit(1)

gp = panel15['gridPos']  # {h:17, w:12, x:12, y:8}
print(f"Panel 15 grid: {gp}")

ds = panel15.get('datasource', {'uid': 'mes_sqlserver'})
original_target = panel15['targets'][0] if panel15.get('targets') else {}

# ─── Define 4 metrics ────────────────────────────────────────────────────────
METRICS = [
    {
        "name": "Elevacion Sin Carga",
        "col_medido":  "TIEMPO_ELEVACION_MEDIDO_SINCARGA",
        "col_min":     "TIEMPO_ELEVACION_MIN_SINCARGA",
        "col_max":     "TIEMPO_ELEVACION_MAX_SINCARGA",
        "default_min": 1.0,
        "default_max": 6.0,
    },
    {
        "name": "Descenso Sin Carga",
        "col_medido":  "TIEMPO_DESCENSO_MEDIDO_SINCARGA",
        "col_min":     "TIEMPO_DESCENSO_MIN_SINCARGA",
        "col_max":     "TIEMPO_DESCENSO_MAX_SINCARGA",
        "default_min": 1.0,
        "default_max": 6.0,
    },
    {
        "name": "Elevacion Con Carga",
        "col_medido":  "TIEMPO_ELEVACION_MEDIDO_CARGA",
        "col_min":     "TIEMPO_ELEVACION_MIN_CARGA",
        "col_max":     "TIEMPO_ELEVACION_MAX_CARGA",
        "default_min": 1.0,
        "default_max": 8.0,
    },
    {
        "name": "Descenso Con Carga",
        "col_medido":  "TIEMPO_DESCENSO_MEDIDO_CARGA",
        "col_min":     "TIEMPO_DESCENSO_MIN_CARGA",
        "col_max":     "TIEMPO_DESCENSO_MAX_CARGA",
        "default_min": 1.0,
        "default_max": 8.0,
    },
]

# ─── Grid layout: 2x2 within the same area as panel 15 ──────────────────────
# Panel 15: x=12, y=8, w=12, h=17
# Split: 2 cols (w=6 each), 2 rows (h=8 each), 1 row gap = 17 total
half_w = gp['w'] // 2   # 6
half_h = gp['h'] // 2   # 8

sub_positions = [
    {"x": gp['x'],           "y": gp['y'],           "w": half_w, "h": half_h},
    {"x": gp['x'] + half_w,  "y": gp['y'],           "w": half_w, "h": half_h},
    {"x": gp['x'],           "y": gp['y'] + half_h,  "w": half_w, "h": half_h + 1},  # +1 for last row
    {"x": gp['x'] + half_w,  "y": gp['y'] + half_h,  "w": half_w, "h": half_h + 1},
]

# ─── Build SQL for each panel (returns 3 cols: value, Min, Max) ──────────────
def make_sql(m):
    # Reuse the same WHERE clause structure as original
    orig_sql = original_target.get('rawSql', '')
    # Extract the FROM/WHERE/ORDER BY part
    from_part = orig_sql[orig_sql.upper().find(' FROM '):]
    return (
        f"SELECT TOP 1 "
        f"COALESCE({m['col_medido']}, 0.0) AS [Valor], "
        f"COALESCE({m['col_min']}, {m['default_min']}) AS [Min], "
        f"COALESCE({m['col_max']}, {m['default_max']}) AS [Max]"
        f"{from_part}"
    )

# ─── Find next available panel IDs ───────────────────────────────────────────
max_id = max(p['id'] for p in dash['panels'])
new_ids = list(range(max_id + 1, max_id + 5))

# ─── Build 4 new gauge panels ────────────────────────────────────────────────
new_panels = []
for i, (m, gpos) in enumerate(zip(METRICS, sub_positions)):
    new_id = new_ids[i]
    sql = make_sql(m)

    target = copy.deepcopy(original_target)
    target['rawSql'] = sql
    target['refId'] = 'A'

    panel = {
        "id": new_id,
        "title": m['name'],
        "type": "gauge",
        "datasource": copy.deepcopy(ds),
        "gridPos": gpos,
        "targets": [target],
        "transformations": [
            {
                "id": "configFromData",
                "options": {
                    "applyTo": {"id": "byName", "options": "Valor"},
                    "configRefId": "A",
                    "mappings": [
                        {
                            "fieldName": "Min",
                            "handlerArguments": {"threshold": {"color": "#2FD06A"}},
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "Max",
                            "handlerArguments": {"threshold": {"color": "#E32636"}},
                            "handlerKey": "threshold2"
                        }
                    ]
                }
            }
        ],
        "options": {
            "showThresholdLabels": True,
            "showThresholdMarkers": True,
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "/^Valor$/",
                "values": False
            },
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": "value",
        },
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "thresholds"},
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "#E32636", "value": None},
                        {"color": "#2FD06A", "value": 3.0},
                        {"color": "#E32636", "value": 5.0}
                    ]
                },
                "unit": "s",
                "decimals": 2,
                "custom": {},
                "mappings": []
            },
            "overrides": []
        }
    }
    new_panels.append(panel)
    print(f"Panel {new_id}: '{m['name']}' at {gpos}")
    print(f"  SQL: {sql[:120]}...")

# ─── Replace panel 15 with the 4 new panels ──────────────────────────────────
dash['panels'] = [p for p in dash['panels'] if p['id'] != 15]
dash['panels'].extend(new_panels)
print(f"\nRemoved panel 15, added panels {new_ids}")

# ─── Push to Grafana ─────────────────────────────────────────────────────────
payload = json.dumps({
    "dashboard": dash,
    "folderId": folder_id,
    "overwrite": True,
    "message": "refactor: 4 individual gauge panels with dynamic min/max scale per metric"
}).encode('utf-8')

req2 = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=payload, headers=headers, method='POST'
)
try:
    with urllib.request.urlopen(req2) as r:
        result = json.loads(r.read())
        print(f"✓ Dashboard pushed: status={result.get('status')}, version={result.get('version')}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code}: {body[:1000]}")
    sys.exit(1)

# ─── Update provisioning JSON ─────────────────────────────────────────────────
prov = "grafana/provisioning/dashboards/oee_dashboard.json"
with open(prov, 'r', encoding='utf-8') as f:
    local = json.load(f)

local['panels'] = [p for p in local['panels'] if p['id'] != 15]
local['panels'].extend(new_panels)

with open(prov, 'w', encoding='utf-8') as f:
    json.dump(local, f, indent=2, ensure_ascii=False)
print(f"✓ Updated {prov}")
print("\nDone! Refresh the dashboard to see 4 individual gauge panels.")
