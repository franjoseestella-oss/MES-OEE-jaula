import json

dashboard_path = 'grafana/provisioning/dashboards/log_dashboard.json'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Find Panel 15
panel_15 = None
for panel in d.get('panels', []):
    if panel.get('id') == 15:
        panel_15 = panel
        break

if not panel_15:
    print("Panel 15 not found!")
    exit(1)

# 1. Update title
panel_15['title'] = "TIEMPOS DE ELEVACIÓN Y DESCENSO — DETALLE DE AGUJA — ${selected_id:text}"

# 2. Update default field configuration (Scale limits 1 to 6, Base: Red, Step 1: Green, Step 2: Red)
panel_15['fieldConfig'] = {
    "defaults": {
        "color": {
            "mode": "thresholds"
        },
        "decimals": 2,
        "min": 1,
        "max": 6,
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {
                    "color": "#E32636", # Red
                    "value": None
                },
                {
                    "color": "#2FD06A", # Green
                    "value": 1.0
                },
                {
                    "color": "#E32636", # Red
                    "value": 6.0
                }
            ]
        },
        "unit": "s"
    }
}

# 3. Update SQL targets
sql_query = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 0.0) AS [Elevacion Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevacion Sin Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 0.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max], "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 0.0) AS [Elevacion Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevacion Con Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 0.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

panel_15['targets'] = [
    {
        "format": "table",
        "rawSql": sql_query,
        "refId": "A"
    }
]

# 4. Set up transformations with handlerArguments colors
panel_15['transformations'] = [
    {
        "id": "configFromData",
        "options": {
            "applyTo": {
                "id": "byName",
                "options": "Elevacion Sin Carga"
            },
            "configRefId": "A",
            "mappings": [
                {
                    "fieldName": "Elevacion Sin Carga Min",
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A" # Green
                        }
                    }
                },
                {
                    "fieldName": "Elevacion Sin Carga Max",
                    "handlerKey": "threshold2",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#E32636" # Red
                        }
                    }
                }
            ]
        }
    },
    {
        "id": "configFromData",
        "options": {
            "applyTo": {
                "id": "byName",
                "options": "Descenso Sin Carga"
            },
            "configRefId": "A",
            "mappings": [
                {
                    "fieldName": "Descenso Sin Carga Min",
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A" # Green
                        }
                    }
                },
                {
                    "fieldName": "Descenso Sin Carga Max",
                    "handlerKey": "threshold2",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#E32636" # Red
                        }
                    }
                }
            ]
        }
    },
    {
        "id": "configFromData",
        "options": {
            "applyTo": {
                "id": "byName",
                "options": "Elevacion Con Carga"
            },
            "configRefId": "A",
            "mappings": [
                {
                    "fieldName": "Elevacion Con Carga Min",
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A" # Green
                        }
                    }
                },
                {
                    "fieldName": "Elevacion Con Carga Max",
                    "handlerKey": "threshold2",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#E32636" # Red
                        }
                    }
                }
            ]
        }
    },
    {
        "id": "configFromData",
        "options": {
            "applyTo": {
                "id": "byName",
                "options": "Descenso Con Carga"
            },
            "configRefId": "A",
            "mappings": [
                {
                    "fieldName": "Descenso Con Carga Min",
                    "handlerKey": "threshold1",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#2FD06A" # Green
                        }
                    }
                },
                {
                    "fieldName": "Descenso Con Carga Max",
                    "handlerKey": "threshold2",
                    "handlerArguments": {
                        "threshold": {
                            "color": "#E32636" # Red
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
                    "Elevacion Sin Carga",
                    "Descenso Sin Carga",
                    "Elevacion Con Carga",
                    "Descenso Con Carga"
                ]
            }
        }
    }
]

with open(dashboard_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Panel 15 updated with color mappings successfully.")
