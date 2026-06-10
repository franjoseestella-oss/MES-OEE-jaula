"""
Refinement: Show actual seconds value on gauge text, keep percentage for color logic.
Use display override to show the measured seconds value instead of the calculated percentage.
This requires the gauge to display the companion 'seconds' field as the value, 
but color according to the pct field.

Better approach: Use the pct field for color logic, but display the real value
by setting a unit=none and using a display expression. OR use Stat panel instead of Gauge.

Actually the cleanest solution in Grafana: use the original seconds field, 
add configFromData mapping to set Min/Max threshold VALUES (not colors - just the 
threshold values from the data) and set FIXED threshold colors in the panel.

The key insight: configFromData threshold1 handler DOES correctly set the threshold VALUE
(that's why the markers appear correctly at 2.85 and 3.48). 
But the COLOR it uses comes from the PANEL's existing threshold steps, not from handlerArguments.

So: if panel has steps [red@null, green@something, red@something_else], 
and configFromData REPLACES step values with dynamic values from data,
the COLORS stay as defined in the panel steps.

So: set panel defaults thresholds to:
  Step 0: red @ null  (base - below min is red)
  Step 1: green @ 1   (placeholder - will be replaced by min value from configFromData)
  Step 2: red @ 6     (placeholder - will be replaced by max value from configFromData)

Then configFromData threshold1 for Min field REPLACES step 1's value (keeps green color)
And configFromData threshold1 for Max field REPLACES step 2's value (keeps red color)

THIS is how it's supposed to work! The colors are preserved from the panel steps,
only the VALUES get updated from the data.

So we need 3 initial threshold steps:
- null: red (base)
- 1.0: green (will be replaced by Min)  
- 6.0: red (will be replaced by Max)
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

# Restore original SQL with measured values + Min/Max columns
sql = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevacion Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevacion Sin Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max], "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevacion Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevacion Con Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

# Key fix: Panel has 3 threshold steps (null:red, 1:green, 6:red)
# configFromData threshold1 UPDATES the value of existing steps in ORDER
# So Min field → updates step[1] value (keeping green), Max field → updates step[2] value (keeping red)
panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "s",
        "min": 0,
        "max": 7,
        "decimals": 2,
        "color": {"mode": "thresholds"},
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},   # step[0]: RED base (< min)
                {"color": "#2FD06A", "value": 1.0},    # step[1]: GREEN at min placeholder
                {"color": "#E32636", "value": 6.0},    # step[2]: RED at max placeholder
            ]
        },
        "mappings": []
    },
    "overrides": []
}

# configFromData for each metric:
# threshold1 for Min → updates step[1] value (green boundary)
# threshold1 for Max → updates step[2] value (red boundary)
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
            "applyTo": {
                "id": "byName",
                "options": field_name
            },
            "mappings": [
                {
                    "fieldName": min_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {"color": "#2FD06A"}  # Green
                    }
                },
                {
                    "fieldName": max_col,
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {"color": "#E32636"}  # Red
                    }
                }
            ]
        }
    })

# Filter to show only measured fields
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
panel_15["options"] = {
    "reduceOptions": {"values": True, "calcs": ["lastNotNull"]},
    "orientation": "auto",
    "showThresholdLabels": True,
    "showThresholdMarkers": True
}

print(f"Threshold steps set: {json.dumps(panel_15['fieldConfig']['defaults']['thresholds']['steps'])}")
print(f"Transformations: {len(panel_15['transformations'])}")

# Push
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Restore seconds display with 3-step thresholds for correct coloring"
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
