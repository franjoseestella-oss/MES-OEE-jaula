"""
Convert panel 15 from Gauge to a combination:
- Keep the gauge visual but show seconds with proper coloring
- Trick: compute the pct for coloring but use the SECONDS as the display value
  by using a "Add field from calculation" transform + setting it as the display field

Actually the cleanest Grafana 10.4 approach:
Use a GAUGE panel with TWO series. For each metric:
  - Field A: the actual seconds (shown as the gauge value text)
  - Field B: the pct (used for threshold color via override)

But gauges don't support this multi-field-per-indicator setup.

REAL FINAL ANSWER: Change panel type to STAT 
- Stat shows the exact value (seconds)
- Colors by threshold (using pct from SQL)
- Shows all 4 values in a 2x2 grid layout
- Looks clean and works 100% reliably
"""
import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"  
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")
print(f"Dashboard version: {dashboard.get('version')}")

panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

# Keep type as GAUGE but use the pct trick with visual improvements:
# The gauge shows the pct value (0-100) in the center
# We override display to show "Elevación SC" labels
# And the visual clearly shows green in the arc range 0-100%
# This is clear and unambiguous

# Better yet: make the gauge show actual seconds AND be colored correctly
# by using a clever SQL trick: return the seconds value but scaled
# such that "within range" = 0-100 and the gauge min/max reflects actual seconds range.
# No - this doesn't work either.

# ACTUAL BEST VISUAL SOLUTION:
# Keep the pct gauge (which DOES work for coloring)
# Show the actual measured seconds value as a LABEL below the gauge
# using a second "text" field that gets shown in the sub-label position

# In Grafana stat panel, we can show multiple fields with "fields" option
# Let's use STAT panel type which is much more flexible for this

panel_15["type"] = "stat"

sql = """SELECT TOP 1 
  COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga],
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

# Stat panel config: shows actual seconds, colored by threshold
# thresholds: red base, green at 1 (placeholder for min), red at 6 (placeholder for max)
panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "s",
        "decimals": 2,
        "color": {"mode": "thresholds"},
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},   # RED base
                {"color": "#2FD06A", "value": 1.0},    # GREEN at min placeholder
                {"color": "#E32636", "value": 6.0},    # RED at max placeholder
            ]
        }
    },
    "overrides": []
}

# Use configFromData to update the threshold values dynamically from Min/Max columns
metrics = [
    ("Elevacion Sin Carga", "Elevacion Sin Carga Min", "Elevacion Sin Carga Max"),
    ("Descenso Sin Carga", "Descenso Sin Carga Min", "Descenso Sin Carga Max"),
    ("Elevacion Con Carga", "Elevacion Con Carga Min", "Elevacion Con Carga Max"),
    ("Descenso Con Carga", "Descenso Con Carga Min", "Descenso Con Carga Max"),
]

transformations = []
for field_name, min_col, max_col in metrics:
    transformations.append({
        "id": "configFromData",
        "options": {
            "configRefId": "A",
            "applyTo": {"id": "byName", "options": field_name},
            "mappings": [
                {
                    "fieldName": min_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {"threshold": {"color": "#2FD06A"}}
                },
                {
                    "fieldName": max_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {"threshold": {"color": "#E32636"}}
                }
            ]
        }
    })

# Only show measured fields
transformations.append({
    "id": "filterFieldsByName",
    "options": {
        "include": {
            "names": [m[0] for m in metrics]
        }
    }
})

panel_15["transformations"] = transformations
panel_15["targets"] = [{"rawSql": sql, "format": "table", "refId": "A"}]

# Stat panel options
panel_15["options"] = {
    "reduceOptions": {"values": True, "calcs": ["lastNotNull"]},
    "orientation": "auto",
    "textMode": "auto",
    "colorMode": "background",  # Color the BACKGROUND of the stat box
    "graphMode": "none",
    "justifyMode": "auto",
    "text": {}
}

print(f"Panel changed to STAT with background color mode")

dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Panel 15: changed to STAT with background coloring"
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
