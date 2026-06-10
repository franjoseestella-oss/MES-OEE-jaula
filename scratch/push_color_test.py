import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# 1. Fetch current dashboard from live Grafana
req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")

panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

if not panel_15:
    print("Panel 15 not found")
    exit(1)

# Configure the field defaults: min=1, max=6
# We set color mode to fixed, and default color to green/red
panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "s",
        "min": 1,
        "max": 6,
        "decimals": 2,
        "color": {
            "mode": "fixed",
            "fixedColor": "#2FD06A"
        }
    },
    "overrides": []
}

# SQL Target: return measured values + calculated color
sql = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga], "
    "CASE WHEN COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) BETWEEN COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AND COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) "
    "     THEN '#2FD06A' ELSE '#E32636' END AS [Elevacion Sin Carga Color], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevacion Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevacion Sin Carga Max], "
    
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "CASE WHEN COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) BETWEEN COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AND COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) "
    "     THEN '#2FD06A' ELSE '#E32636' END AS [Descenso Sin Carga Color], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max], "
    
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga], "
    "CASE WHEN COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) BETWEEN COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AND COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) "
    "     THEN '#2FD06A' ELSE '#E32636' END AS [Elevacion Con Carga Color], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevacion Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevacion Con Carga Max], "
    
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "CASE WHEN COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) BETWEEN COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AND COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) "
    "     THEN '#2FD06A' ELSE '#E32636' END AS [Descenso Con Carga Color], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

metrics = [
    ("Elevacion Sin Carga", "Elevacion Sin Carga Color"),
    ("Descenso Sin Carga", "Descenso Sin Carga Color"),
    ("Elevacion Con Carga", "Elevacion Con Carga Color"),
    ("Descenso Con Carga", "Descenso Con Carga Color"),
]

transformations = []
for field_name, color_col in metrics:
    transformations.append({
        "id": "configFromData",
        "options": {
            "configRefId": "A",
            "applyTo": {"id": "byName", "options": field_name},
            "mappings": [
                {
                    "fieldName": color_col,
                    "handlerKey": "color"
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
    "showThresholdLabels": False,
    "showThresholdMarkers": False,
    "text": {}
}

# Prepare dashboard payload
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Fixed color configuration based on range"
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
