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

# 1. Load from local provisioning file
filepath = 'grafana/provisioning/dashboards/log_dashboard.json'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    dashboard = json.load(f)

print(f"Loaded local dashboard: version {dashboard.get('version')}")

# 2. Modify panels list
panels = dashboard.get('panels', [])

# Find panel 10 (OEE GLOBAL)
panel_10 = None
for p in panels:
    if p.get('id') == 10:
        panel_10 = p
        break

if not panel_10:
    print("Error: Panel 10 (OEE GLOBAL) not found")
    exit(1)

# Modify Panel 10 to be a single combined BARGAUGE panel
panel_10["type"] = "bargauge"
panel_10["gridPos"] = {"h": 4, "w": 24, "x": 0, "y": 0}
panel_10["title"] = "OEE GLOBAL & MÉTRICAS DE EFICIENCIA"

# SQL Query returning OEE GLOBAL, Objetivo OEE, and the other metrics
panel_10["targets"] = [
    {
        "datasource": {
            "type": "mssql",
            "uid": "mes_sqlserver"
        },
        "editorMode": "code",
        "format": "table",
        "rawQuery": True,
        "rawSql": "SELECT COALESCE((SELECT TOP 1 oee * 100 FROM mes_oee_snapshots WHERE oee IS NOT NULL ORDER BY ts DESC), 0.0) AS [OEE GLOBAL], TRY_CAST(COALESCE(NULLIF(TRIM('${objetivo_oee}'), ''), '85') AS FLOAT) AS [Objetivo OEE], COALESCE((SELECT TOP 1 availability * 100 FROM mes_oee_snapshots WHERE availability IS NOT NULL ORDER BY ts DESC), 0.0) AS [Disponibilidad], COALESCE((SELECT TOP 1 performance * 100 FROM mes_oee_snapshots WHERE performance IS NOT NULL ORDER BY ts DESC), 0.0) AS [Rendimiento], COALESCE((SELECT TOP 1 quality * 100 FROM mes_oee_snapshots WHERE quality IS NOT NULL ORDER BY ts DESC), 0.0) AS [Calidad]",
        "refId": "A"
    }
]

# Field Config: defaults for OEE GLOBAL thresholds (dynamic), overrides for others
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
                    "color": "#E32636",  # Red below target
                    "value": None
                },
                {
                    "color": "#2FD06A",  # Green above/at target
                    "value": 85.0        # Default placeholder, will be replaced by mapping
                }
            ]
        },
        "unit": "percent"
    },
    "overrides": [
        {
            "matcher": {
                "id": "byName",
                "options": "Disponibilidad"
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
                                "value": 80.0
                            },
                            {
                                "color": "#2FD06A",
                                "value": 90.0
                            }
                        ]
                    }
                }
            ]
        },
        {
            "matcher": {
                "id": "byName",
                "options": "Rendimiento"
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
                                "value": 80.0
                            },
                            {
                                "color": "#2FD06A",
                                "value": 90.0
                            }
                        ]
                    }
                }
            ]
        },
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
}

# Transformations: map Objetivo OEE to threshold1 of OEE GLOBAL, filter fields
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
                    "OEE GLOBAL",
                    "Disponibilidad",
                    "Rendimiento",
                    "Calidad"
                ]
            }
        }
    }
]

# Options for Bar Gauge
panel_10["options"] = {
    "displayMode": "gradient",
    "maxVizHeight": 300,
    "minVizHeight": 16,
    "minVizWidth": 8,
    "namePlacement": "auto",
    "orientation": "horizontal",
    "reduceOptions": {
        "calcs": [
            "lastNotNull"
        ],
        "fields": "",
        "values": True
    },
    "showUnfilled": True,
    "sizing": "auto",
    "valueMode": "color"
}

# Filter out Panel 11 (METRICAS OEE) since it is now integrated into Panel 10
filtered_panels = [p for p in panels if p.get('id') != 11]
dashboard['panels'] = filtered_panels

print(f"Filtered panels count: {len(filtered_panels)} (was {len(panels)})")

# Remove ID/Version for pushing
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Integrate OEE and all metrics into a single bargauge panel"
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
