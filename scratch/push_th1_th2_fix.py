"""
Root cause found: Both Min and Max were mapped to "threshold1"
so Max overwrites Min in the threshold steps array.

Fix: 
- steps[0]: null -> RED (base)
- steps[1]: 1.0 -> GREEN  <- threshold1 (updated by Min field)
- steps[2]: 6.0 -> RED    <- threshold2 (updated by Max field)

Map Min -> threshold1, Max -> threshold2
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

# Restore GAUGE type
panel_15["type"] = "gauge"

# Panel thresholds: 3 steps so threshold1 = step[1] and threshold2 = step[2]
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
                {"color": "#E32636", "value": None},  # step[0] base RED (< min)
                {"color": "#2FD06A", "value": 1.0},   # step[1] threshold1 GREEN placeholder -> updated by Min
                {"color": "#E32636", "value": 6.0},   # step[2] threshold2 RED placeholder -> updated by Max
            ]
        },
        "mappings": []
    },
    "overrides": []
}

# SQL: return measured values + Min + Max columns (Min before Max!)
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

# configFromData: Min -> threshold1, Max -> threshold2
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
                    "handlerKey": "threshold1",   # -> updates step[1] GREEN
                    "handlerArguments": {}
                },
                {
                    "fieldName": max_col,
                    "handlerKey": "threshold2",   # -> updates step[2] RED
                    "handlerArguments": {}
                }
            ]
        }
    })

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
    "showThresholdMarkers": True,
    "text": {}
}

print("threshold1 for Min, threshold2 for Max -> different steps, no overwrite")

dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Fix: threshold1=Min (green), threshold2=Max (red)"
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
