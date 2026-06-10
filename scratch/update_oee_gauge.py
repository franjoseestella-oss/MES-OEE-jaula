import json
import urllib.request
import urllib.error
import base64
import os

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# 1. Load from local provisioning file (which we just refreshed from live)
filepath = 'grafana/provisioning/dashboards/log_dashboard.json'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    dashboard = json.load(f)

print(f"Loaded local dashboard: version {dashboard.get('version')}")

# 2. Modify panels list
panels = dashboard.get('panels', [])

# Find panel 10 (OEE GLOBAL)
panel_10 = None
# Find panel 11 (METRICAS OEE)
panel_11 = None

for p in panels:
    if p.get('id') == 10:
        panel_10 = p
    elif p.get('id') == 11:
        panel_11 = p

if not panel_10:
    print("Error: Panel 10 (OEE GLOBAL) not found")
    exit(1)
if not panel_11:
    print("Error: Panel 11 (METRICAS OEE) not found")
    exit(1)

# Modify Panel 10 to be a GAUGE with dynamic threshold based on Objetivo OEE
panel_10["type"] = "gauge"
panel_10["gridPos"] = {"h": 4, "w": 10, "x": 0, "y": 0}
panel_10["title"] = "OEE GLOBAL"

# Targets: return OEE GLOBAL value and Objetivo OEE
panel_10["targets"] = [
    {
        "datasource": {
            "type": "mssql",
            "uid": "mes_sqlserver"
        },
        "editorMode": "code",
        "format": "table",
        "rawQuery": True,
        "rawSql": "SELECT COALESCE((SELECT TOP 1 oee * 100 FROM mes_oee_snapshots WHERE oee IS NOT NULL ORDER BY ts DESC), 0.0) AS [OEE GLOBAL], TRY_CAST(COALESCE(NULLIF(TRIM('${objetivo_oee}'), ''), '85') AS FLOAT) AS [Objetivo OEE]",
        "refId": "A"
    }
]

# Field Config: Base=Red, Step 1 = Green (dynamic)
panel_10["fieldConfig"] = {
    "defaults": {
        "color": {
            "mode": "thresholds"
        },
        "decimals": 1,
        "mappings": [],
        "max": 100,
        "min": 0,
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {
              "color": "#E32636",
              "value": None
            },
            {
              "color": "#2FD06A",
              "value": 85.0
            }
          ]
        },
        "unit": "percent"
    },
    "overrides": []
}

# Transformations: configFromData map Objetivo OEE to threshold1 (Green step)
panel_10["transformations"] = [
    {
        "id": "configFromData",
        "options": {
            "configRefId": "A",
            "applyTo": {
                "id": "byName",
                "options": "OEE GLOBAL"
            },
            "mappings": [
                {
                    "fieldName": "Objetivo OEE",
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A"
                        }
                    }
                }
            ]
        }
    },
    {
        "id": "filterFieldsByName",
        "options": {
            "include": {
                "names": [
                    "OEE GLOBAL"
                ]
            }
        }
    }
]

# Options for Gauge
panel_10["options"] = {
    "minVizHeight": 75,
    "minVizWidth": 75,
    "orientation": "auto",
    "reduceOptions": {
        "calcs": [
            "lastNotNull"
        ],
        "fields": "",
        "values": False
    },
    "showThresholdLabels": False,
    "showThresholdMarkers": True,
    "sizing": "auto"
}

# Modify Panel 11 (METRICAS OEE)
# Set grid position to take the remaining width in the top row: w=14, x=10
panel_11["gridPos"] = {"h": 4, "w": 14, "x": 10, "y": 0}

# Add field overrides to set Calidad threshold specifically (orange 90, green 98)
panel_11["fieldConfig"]["overrides"] = [
    {
        "matcher": {
            "id": "byName",
            "options": "Calidad"
        },
        "properties": [
            {
                "id": "thresholds",
                "value": {
                    "mode": "absolute",
                    "steps": [
                        {
                            "color": "#E32636",
                            "value": None
                        },
                        {
                            "color": "#F4A623",
                            "value": 90.0
                        },
                        {
                            "color": "#2FD06A",
                            "value": 98.0
                        }
                    ]
                }
            }
        ]
    }
]

# Filter out Panel 12 (RENDIMIENTO) and Panel 13 (CALIDAD)
filtered_panels = [p for p in panels if p.get('id') not in (12, 13)]
dashboard['panels'] = filtered_panels

print(f"Filtered panels count: {len(filtered_panels)} (was {len(panels)})")

# Remove ID/Version for pushing
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Convert OEE GLOBAL to Gauge with dynamic threshold and layout OEE metrics in single top row"
}

# 3. Post to Grafana
data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data, headers=headers, method="POST"
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"Dashboard pushed to Grafana. Status: {result.get('status')}")
        
        # 4. Fetch the final updated dashboard with new version/ID to save locally
        req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
        with urllib.request.urlopen(req_get) as resp_get:
            existing = json.loads(resp_get.read().decode("utf-8"))
            final_dashboard = existing["dashboard"]
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(final_dashboard, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved updated dashboard to {filepath}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
