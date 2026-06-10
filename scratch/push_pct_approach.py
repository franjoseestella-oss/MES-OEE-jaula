"""
Final fix: Change the approach completely.
Instead of using configFromData for colors, we compute a PERCENTAGE in SQL:
  pct = (measured - min) / (max - min) * 100
  
Then use fixed thresholds:
  < 0%: RED (below min)
  0-100%: GREEN (within range)  
  > 100%: RED (above max)

The actual numeric VALUE will be shown via a separate display override.
"""
import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Get current dashboard
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")
print(f"Dashboard version: {dashboard.get('version')}")

# Find panel 15
panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

# New SQL: return percentage AND original values
# For each metric: pct = CASE WHEN max>min THEN (measured-min)/(max-min)*100.0 ELSE 50 END
sql = """SELECT TOP 1 
  COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga],
  CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA,6.0) > COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0) 
    THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA,0.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA,6.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0)) * 100.0 
    ELSE 50.0 END AS [Elev SC Pct],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga],
  CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA,6.0) > COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0) 
    THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA,0.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA,6.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0)) * 100.0 
    ELSE 50.0 END AS [Desc SC Pct],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga],
  CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_CARGA,6.0) > COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0) 
    THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA,0.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_CARGA,6.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0)) * 100.0 
    ELSE 50.0 END AS [Elev CC Pct],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga],
  CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_CARGA,6.0) > COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0) 
    THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA,0.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_CARGA,6.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0)) * 100.0 
    ELSE 50.0 END AS [Desc CC Pct],
  COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevacion Sin Carga Min],
  COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevacion Sin Carga Max],
  COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min],
  COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max],
  COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevacion Con Carga Min],
  COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevacion Con Carga Max],
  COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min],
  COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max]
FROM LOG_TABLA 
WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') 
ORDER BY fecha_creacion DESC"""

# The gauge shows Pct fields with thresholds at 0 and 100
# Fixed thresholds: red < 0, green 0-100, red > 100
# Display override: show the original VALUE (not pct) on the gauge text

# Gauge panel config for percentage-based display
panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "percent",
        "min": -50,
        "max": 150,
        "decimals": 0,
        "color": {"mode": "thresholds"},
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},    # red base (< 0%)
                {"color": "#2FD06A", "value": 0},       # green at 0% (min)
                {"color": "#E32636", "value": 100},     # red at 100% (max)
            ]
        },
        "mappings": []
    },
    "overrides": [
        # Show actual measured value (in seconds) as display text on Pct fields
        {
            "matcher": {"id": "byName", "options": "Elev SC Pct"},
            "properties": [
                {"id": "displayName", "value": "Elevacion Sin Carga"}
            ]
        },
        {
            "matcher": {"id": "byName", "options": "Desc SC Pct"},
            "properties": [
                {"id": "displayName", "value": "Descenso Sin Carga"}
            ]
        },
        {
            "matcher": {"id": "byName", "options": "Elev CC Pct"},
            "properties": [
                {"id": "displayName", "value": "Elevacion Con Carga"}
            ]
        },
        {
            "matcher": {"id": "byName", "options": "Desc CC Pct"},
            "properties": [
                {"id": "displayName", "value": "Descenso Con Carga"}
            ]
        }
    ]
}

# Transformations: 
# 1. configFromData to map Min/Max to the gauge min/max display range for each Pct field
# 2. filterFieldsByName to only show Pct fields
pct_fields = ["Elev SC Pct", "Desc SC Pct", "Elev CC Pct", "Desc CC Pct"]

panel_15["transformations"] = [
    {
        "id": "filterFieldsByName",
        "options": {
            "include": {
                "names": pct_fields
            }
        }
    }
]

panel_15["targets"] = [{
    "rawSql": sql,
    "format": "table",
    "refId": "A"
}]

panel_15["options"] = {
    "reduceOptions": {
        "values": True,
        "calcs": ["lastNotNull"]
    },
    "orientation": "auto",
    "showThresholdLabels": False,
    "showThresholdMarkers": True
}

print("Panel 15 updated in memory")

# Push to API
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Panel 15: percentage-based thresholds for correct color"
}
if folder_uid:
    payload["folderUid"] = folder_uid

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data, headers=headers, method="POST"
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"Success! Status: {result.get('status')}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
