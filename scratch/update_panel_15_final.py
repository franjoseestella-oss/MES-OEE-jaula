import json

DASHBOARD_FILE = r"grafana\provisioning\dashboards\log_dashboard.json"

with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

# Increment version
if dashboard.get("version") is not None:
    dashboard["version"] += 1

# Locate panel 15
panel_15 = None
for panel in dashboard.get("panels", []):
    if panel.get("id") == 15:
        panel_15 = panel
        break

if not panel_15:
    print("Error: Panel 15 not found in dashboard JSON!")
    exit(1)

# 1. Update SQL target query to select Límite Máximo Gauge
target_sql = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevación Sin Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 0.0) AS [Elevación Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 8.0) AS [Elevación Sin Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 0.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 8.0) AS [Descenso Sin Carga Max], "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevación Con Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 0.0) AS [Elevación Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 8.0) AS [Elevación Con Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 0.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 8.0) AS [Descenso Con Carga Max], "
    "8.0 AS [Límite Máximo Gauge] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

panel_15["targets"][0]["rawSql"] = target_sql

# 2. Update panel fieldConfig defaults
panel_15["fieldConfig"]["defaults"]["min"] = 0
panel_15["fieldConfig"]["defaults"]["max"] = 8
panel_15["fieldConfig"]["defaults"]["decimals"] = 2
panel_15["fieldConfig"]["defaults"]["unit"] = "s"
panel_15["fieldConfig"]["defaults"]["color"] = { "mode": "thresholds" }

# Set default thresholds: Base (Red), Step 1 (Green, 3.0), Step 2 (Red, 5.0)
panel_15["fieldConfig"]["defaults"]["thresholds"] = {
    "mode": "absolute",
    "steps": [
        {
            "color": "#E32636",  # Red
            "value": None
        },
        {
            "color": "#2FD06A",  # Green
            "value": 3.0
        },
        {
            "color": "#E32636",  # Red
            "value": 5.0
        }
    ]
}

# 3. Reconstruct transformations
gauges = [
    ("Elevación Sin Carga", "Elevación Sin Carga Min", "Elevación Sin Carga Max"),
    ("Descenso Sin Carga", "Descenso Sin Carga Min", "Descenso Sin Carga Max"),
    ("Elevación Con Carga", "Elevación Con Carga Min", "Elevación Con Carga Max"),
    ("Descenso Con Carga", "Descenso Con Carga Min", "Descenso Con Carga Max")
]

transformations = []
for gauge_name, min_field, max_field in gauges:
    transformations.append({
        "id": "configFromData",
        "options": {
            "applyTo": {
                "id": "byName",
                "options": gauge_name
            },
            "configRefId": "A",
            "mappings": [
                {
                    "fieldName": min_field,
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A"  # Green
                        }
                    }
                },
                {
                    "fieldName": max_field,
                    "handlerKey": "threshold2",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#E32636"  # Red
                        }
                    }
                },
                {
                    "fieldName": "Límite Máximo Gauge",
                    "handlerKey": "max"
                }
            ]
        }
    })

# Append filterFieldsByName transformation
transformations.append({
    "id": "filterFieldsByName",
    "options": {
        "include": {
            "names": [g[0] for g in gauges]
        }
    }
})

panel_15["transformations"] = transformations

with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print("Panel 15 configuration successfully updated in log_dashboard.json.")
