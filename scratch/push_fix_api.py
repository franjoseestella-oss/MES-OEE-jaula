"""
Fix panel 15 permanently using Python to modify and push via Grafana API.
This bypasses the OneDrive file sync issue completely.

New approach: Use a single red base threshold + configFromData (ONE transformation, no applyTo)
that maps Min → threshold1 (green) and Max → threshold1 (red) for ALL fields simultaneously.
"""
import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json",
}

# Step 1: Get current dashboard from API
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1",
    headers=headers,
)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")
print(f"Got dashboard: {dashboard['title']}, version {dashboard.get('version')}")

# Step 2: Find and fix panel 15
panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

if not panel_15:
    print("ERROR: Panel 15 not found!")
    exit(1)

print(f"Before fix - min: {panel_15['fieldConfig']['defaults']['min']}, max: {panel_15['fieldConfig']['defaults']['max']}")

# Fix min/max display range
panel_15["fieldConfig"]["defaults"]["min"] = 1
panel_15["fieldConfig"]["defaults"]["max"] = 6

# Fix default thresholds - single red base step (configFromData will add the rest dynamically)
panel_15["fieldConfig"]["defaults"]["thresholds"] = {
    "mode": "absolute",
    "steps": [
        {"color": "#E32636", "value": None}  # Red base (< min)
    ]
}

# Fix transformations - replace all configFromData with correct ones
# Each one: applyTo byName for the specific field, maps Min→green (threshold1), Max→red (threshold1)
metrics = [
    ("Elevación Sin Carga", "Elevación Sin Carga Min", "Elevación Sin Carga Max"),
    ("Descenso Sin Carga", "Descenso Sin Carga Min", "Descenso Sin Carga Max"),
    ("Elevación Con Carga", "Elevación Con Carga Min", "Elevación Con Carga Max"),
    ("Descenso Con Carga", "Descenso Con Carga Min", "Descenso Con Carga Max"),
]

new_transformations = []
for field_name, min_col, max_col in metrics:
    new_transformations.append({
        "id": "configFromData",
        "options": {
            "configRefId": "A",
            "applyTo": {
                "id": "byName",
                "options": field_name
            },
            "mappings": [
                {
                    "fieldName": min_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {"color": "#2FD06A"}  # Green for Min
                    }
                },
                {
                    "fieldName": max_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {"color": "#E32636"}  # Red for Max
                    }
                }
            ]
        }
    })

# Add filter at the end - only show the 4 measured fields
new_transformations.append({
    "id": "filterFieldsByName",
    "options": {
        "include": {
            "names": [m[0] for m in metrics]
        }
    }
})

panel_15["transformations"] = new_transformations

# Fix SQL - ensure Min and Max columns are in the right order (Min before Max!)
# Also fix COALESCE defaults to use reasonable values (1 for min, 6 for max)
sql = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevación Sin Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevación Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevación Sin Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max], "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevación Con Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevación Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevación Con Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

panel_15["targets"] = [{
    "rawSql": sql,
    "format": "table",
    "refId": "A"
}]

print(f"After fix - min: {panel_15['fieldConfig']['defaults']['min']}, max: {panel_15['fieldConfig']['defaults']['max']}")
print(f"Transformations: {len(panel_15['transformations'])}")
print(f"SQL starts: {sql[:100]}...")

# Step 3: Push to Grafana API
# Remove id to allow update, set overwrite=True
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None  # Let Grafana handle versioning

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Fix panel 15 gauge thresholds - green when within range"
}
if folder_uid:
    payload["folderUid"] = folder_uid

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data,
    headers=headers,
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"\nSuccess! Status: {result.get('status')}, URL: {result.get('url')}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    print(f"Error {e.code}: {error_body}")

# Step 4: Verify
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1",
    headers=headers,
)
with urllib.request.urlopen(req) as resp:
    verify = json.loads(resp.read().decode("utf-8"))
p = [x for x in verify["dashboard"]["panels"] if x.get("id") == 15][0]
print(f"\nVerify from API:")
print(f"  min: {p['fieldConfig']['defaults']['min']}")
print(f"  max: {p['fieldConfig']['defaults']['max']}")
print(f"  thresholds: {json.dumps(p['fieldConfig']['defaults']['thresholds'])}")
print(f"  transformations: {len(p.get('transformations', []))}")
