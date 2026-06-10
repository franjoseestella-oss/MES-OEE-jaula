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

# Find or recreate Panel 10 (OEE GLOBAL) and Panel 11 (METRICAS OEE)
panel_10 = None
panel_11 = None
other_panels = []

for p in panels:
    if p.get('id') == 10:
        panel_10 = p
    elif p.get('id') == 11:
        panel_11 = p
    elif p.get('id') not in (12, 13):  # Exclude old RENDIMIENTO and CALIDAD panels
        other_panels.append(p)

if not panel_10:
    panel_10 = {"id": 10}
if not panel_11:
    panel_11 = {"id": 11}

# Configure Panel 10 as a GAUGE
panel_10["title"] = "OEE GLOBAL"
panel_10["type"] = "gauge"
panel_10["gridPos"] = {"h": 4, "w": 10, "x": 0, "y": 0}
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

# Configure Panel 11 as a BARGAUGE for Availability, Performance, Quality
panel_11["title"] = "METRICAS OEE"
panel_11["type"] = "bargauge"
panel_11["gridPos"] = {"h": 4, "w": 14, "x": 10, "y": 0}
panel_11["targets"] = [
    {
        "datasource": {
            "type": "mssql",
            "uid": "mes_sqlserver"
        },
        "editorMode": "code",
        "format": "table",
        "rawQuery": True,
        "rawSql": "SELECT COALESCE((SELECT TOP 1 availability * 100 FROM mes_oee_snapshots WHERE availability IS NOT NULL ORDER BY ts DESC), 0.0) AS [Disponibilidad], COALESCE((SELECT TOP 1 performance * 100 FROM mes_oee_snapshots WHERE performance IS NOT NULL ORDER BY ts DESC), 0.0) AS [Rendimiento], COALESCE((SELECT TOP 1 quality * 100 FROM mes_oee_snapshots WHERE quality IS NOT NULL ORDER BY ts DESC), 0.0) AS [Calidad]",
        "refId": "A"
    }
]
panel_11["fieldConfig"] = {
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
                    "color": "#F4A623",
                    "value": 80.0
                },
                {
                    "color": "#2FD06A",
                    "value": 90.0
                }
            ]
        },
        "unit": "percent"
    },
    "overrides": [
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
panel_11["options"] = {
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
panel_11["transformations"] = []

# Reassemble panels list
new_panels = [panel_10, panel_11] + other_panels
dashboard['panels'] = new_panels

# Add/ensure variable
templating = dashboard.get('templating', {})
list_vars = templating.get('list', [])

# Remove existing objetivo_oee variable if any to prevent duplicate
list_vars = [v for v in list_vars if v.get('name') != 'objetivo_oee']

# Append variable definition
list_vars.append({
    "current": {
        "selected": False,
        "text": "85",
        "value": "85"
    },
    "hide": 0,
    "label": "Objetivo OEE (%)",
    "name": "objetivo_oee",
    "options": [
        {
            "selected": True,
            "text": "85",
            "value": "85"
        }
    ],
    "query": "85",
    "skipUrlSync": False,
    "type": "textbox"
})

templating['list'] = list_vars
dashboard['templating'] = templating

# Remove ID/Version for pushing
dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Revert to Gauge for OEE GLOBAL, with METRICAS OEE as a bargauge next to it"
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
