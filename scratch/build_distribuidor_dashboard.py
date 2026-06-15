import json
import urllib.request
import urllib.error
import base64
import sys

GRAFANA_URL  = "http://localhost:3010"
GRAFANA_USER = "fran.jose.estella@gmail.com"
GRAFANA_PASS = "admin123"
DASHBOARD_UID = "mes-oee-v2"
DATASOURCE_UID = "mes_sqlserver"

# Helper to build percentage gauge panel displaying all 4 gauges side-by-side
def build_pct_gauge_panel(panel_id, title, sql_query, grid_pos):
    return {
        "datasource": {
            "type": "mssql",
            "uid": DATASOURCE_UID
        },
        "fieldConfig": {
            "defaults": {
                "color": {
                    "mode": "thresholds"
                },
                "decimals": 1,
                "mappings": [],
                "max": 200,
                "min": -100,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {
                            "color": "#E32636", # Red (<0%)
                            "value": None
                        },
                        {
                            "color": "#2FD06A", # Green (0-100%)
                            "value": 0
                        },
                        {
                            "color": "#E32636", # Red (>100%)
                            "value": 100
                        }
                    ]
                },
                "unit": "percent"
            },
            "overrides": []
        },
        "gridPos": grid_pos,
        "id": panel_id,
        "options": {
            "colorMode": "value",
            "minVizHeight": 75,
            "minVizWidth": 75,
            "orientation": "auto",
            "reduceOptions": {
                "calcs": [
                    "lastNotNull"
                ],
                "fields": "/^(Elevación|Descenso) (Con|Sin) Carga$/",
                "values": False
            },
            "showThresholdLabels": False,
            "showThresholdMarkers": True,
            "sizing": "auto",
            "textMode": "auto"
        },
        "targets": [
            {
                "format": "table",
                "rawSql": sql_query,
                "refId": "A"
            }
        ],
        "title": title,
        "type": "gauge"
    }

# Helper to build seconds gauge panel displaying 4 gauges side-by-side with dynamic thresholds
def build_sec_gauge_panel(panel_id, title, sql_query, grid_pos):
    return {
        "datasource": {
            "type": "mssql",
            "uid": DATASOURCE_UID
        },
        "fieldConfig": {
            "defaults": {
                "color": {
                    "mode": "thresholds"
                },
                "decimals": 2,
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {
                            "color": "#E32636",
                            "value": None
                        },
                        {
                            "color": "#2FD06A",
                            "value": 3
                        },
                        {
                            "color": "#E32636",
                            "value": 5
                        }
                    ]
                },
                "unit": "s"
            },
            "overrides": []
        },
        "gridPos": grid_pos,
        "id": panel_id,
        "options": {
            "colorMode": "value",
            "minVizHeight": 75,
            "minVizWidth": 75,
            "orientation": "auto",
            "reduceOptions": {
                "calcs": [
                    "lastNotNull"
                ],
                "fields": "/^(Elevación|Descenso) (Con|Sin) Carga$/",
                "values": False
            },
            "showThresholdLabels": True,
            "showThresholdMarkers": True,
            "sizing": "auto",
            "textMode": "auto"
        },
        "targets": [
            {
                "format": "table",
                "rawSql": sql_query,
                "refId": "A"
            }
        ],
        "transformations": [
            {
                "id": "configFromData",
                "options": {
                    "applyTo": {
                        "id": "byName",
                        "options": "Elevación Con Carga"
                    },
                    "configRefId": "A",
                    "mappings": [
                        {
                            "fieldName": "Elevación Con Carga Min",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            },
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "Elevación Con Carga Max",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            },
                            "handlerKey": "threshold2"
                        }
                    ]
                }
            },
            {
                "id": "configFromData",
                "options": {
                    "applyTo": {
                        "id": "byName",
                        "options": "Elevación Sin Carga"
                    },
                    "configRefId": "A",
                    "mappings": [
                        {
                            "fieldName": "Elevación Sin Carga Min",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            },
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "Elevación Sin Carga Max",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            },
                            "handlerKey": "threshold2"
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
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            },
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "Descenso Con Carga Max",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            },
                            "handlerKey": "threshold2"
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
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            },
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "Descenso Sin Carga Max",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            },
                            "handlerKey": "threshold2"
                        }
                    ]
                }
            }
        ],
        "title": title,
        "type": "gauge"
    }

def build_row(panel_id, title, grid_pos):
    return {
        "collapsed": False,
        "gridPos": grid_pos,
        "id": panel_id,
        "panels": [],
        "title": title,
        "type": "row"
    }

def main():
    # 1. Base query blocks for percentage calculations
    def get_hist_pct_query(family_cond):
        return f"""
        SELECT 
          AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) 
            THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Elevación Con Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) 
            THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Elevación Sin Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) 
            THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Descenso Con Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) 
            THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Descenso Sin Carga]
        FROM LOG_TABLA 
        WHERE OK_NOK = 'OK'
          AND {family_cond}
          AND $__timeFilter(fecha_creacion)
        """

    def get_recent_pct_query(family_cond):
        return f"""
        WITH Last50 AS (
            SELECT TOP 50 *
            FROM LOG_TABLA
            WHERE OK_NOK = 'OK'
              AND {family_cond}
              ORDER BY fecha_creacion DESC
        )
        SELECT 
          AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) 
            THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Elevación Con Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) 
            THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Elevación Sin Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) 
            THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Descenso Con Carga],
          AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) 
            THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) * 100.0 
            ELSE 50.0 END) AS [Descenso Sin Carga]
        FROM Last50
        """

    def get_bastidor_sec_query():
        return """
        SELECT TOP 1
          COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevación Con Carga],
          COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevación Con Carga Min],
          COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevación Con Carga Max],
          
          COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevación Sin Carga],
          COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevación Sin Carga Min],
          COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevación Sin Carga Max],
          
          COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga],
          COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min],
          COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max],
          
          COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga],
          COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min],
          COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max]
        FROM LOG_TABLA
        WHERE NBASTIDOR = '${selected_bastidor}'
        ORDER BY fecha_creacion DESC
        """

    families = {
        "M11": "(NMODELO LIKE 'FD%' OR NMODELO LIKE 'FG%')",
        "XL": "(NMODELO LIKE 'XL%')",
        "M2": "(NMODELO LIKE 'MX%')"
    }

    panels = []
    pid_counter = 100

    # ─────────────────────────────────────────────────────────────────────────
    # BLOQUE 1: ANALISIS GENERAL POR HISTORICO
    # ─────────────────────────────────────────────────────────────────────────
    panels.append(build_row(pid_counter, "📊 BLOQUE 1: ANÁLISIS GENERAL POR HISTÓRICO Y PERIODO (Filtro por Fecha - Solo OK)", {"h": 1, "w": 24, "x": 0, "y": 0}))
    pid_counter += 1

    y_pos = 1
    for fam_name, fam_cond in families.items():
        panels.append(build_row(pid_counter, f"⚙️ Histórico - Familia {fam_name}", {"h": 1, "w": 24, "x": 0, "y": y_pos}))
        pid_counter += 1
        y_pos += 1

        sql = get_hist_pct_query(fam_cond)
        grid = {"h": 6, "w": 24, "x": 0, "y": y_pos}
        panels.append(build_pct_gauge_panel(pid_counter, f"Regulación de Ciclos - {fam_name} (%)", sql, grid))
        pid_counter += 1
        y_pos += 6

    # ─────────────────────────────────────────────────────────────────────────
    # BLOQUE 2: ANALISIS UNITARIO POR BASTIDOR
    # ─────────────────────────────────────────────────────────────────────────
    panels.append(build_row(pid_counter, "🔍 BLOQUE 2: ANÁLISIS UNITARIO POR BASTIDOR", {"h": 1, "w": 24, "x": 0, "y": y_pos}))
    pid_counter += 1
    y_pos += 1

    sql = get_bastidor_sec_query()
    grid = {"h": 6, "w": 24, "x": 0, "y": y_pos}
    panels.append(build_sec_gauge_panel(pid_counter, "Tiempos Medidos y Límites (Segundos)", sql, grid))
    pid_counter += 1
    y_pos += 6

    # ─────────────────────────────────────────────────────────────────────────
    # BLOQUE 3: ESTABILIDAD RECIENTE
    # ─────────────────────────────────────────────────────────────────────────
    panels.append(build_row(pid_counter, "📈 BLOQUE 3: ESTABILIDAD RECIENTE (Promedio Últimas 50 Carretillas OK)", {"h": 1, "w": 24, "x": 0, "y": y_pos}))
    pid_counter += 1
    y_pos += 1

    for fam_name, fam_cond in families.items():
        panels.append(build_row(pid_counter, f"⚡ Reciente - Familia {fam_name}", {"h": 1, "w": 24, "x": 0, "y": y_pos}))
        pid_counter += 1
        y_pos += 1

        sql = get_recent_pct_query(fam_cond)
        grid = {"h": 6, "w": 24, "x": 0, "y": y_pos}
        panels.append(build_pct_gauge_panel(pid_counter, f"Estabilidad de Ciclos - {fam_name} (%)", sql, grid))
        pid_counter += 1
        y_pos += 6

    # Load existing template to preserve metadata like links, tags, etc.
    with open('grafana/provisioning/dashboards/distribuidor_dashboard.json', encoding='utf-8') as f:
        existing = json.load(f)

    # Re-build dashboard JSON structure
    dashboard = {
        "annotations": existing.get("annotations", {"list": []}),
        "description": "Rediseño de Pantalla Distribuidor y KPIs - MES-OEE Jaula Elevación",
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "id": existing.get("id", 12),
        "links": existing.get("links", []),
        "panels": panels,
        "schemaVersion": existing.get("schemaVersion", 36),
        "style": "dark",
        "tags": ["log", "mes", "oee", "pruebas"],
        "templating": {
            "list": [
                {
                    "current": {
                        "selected": True,
                        "value": "SFB09E704641",
                        "text": "SFB09E704641"
                    },
                    "datasource": {
                        "type": "mssql",
                        "uid": DATASOURCE_UID
                    },
                    "definition": "SELECT NBASTIDOR FROM (SELECT DISTINCT NBASTIDOR, MAX(fecha_creacion) as max_f FROM LOG_TABLA GROUP BY NBASTIDOR) AS t ORDER BY max_f DESC",
                    "hide": 0,
                    "includeAll": False,
                    "label": "Bastidor",
                    "multi": False,
                    "name": "selected_bastidor",
                    "options": [],
                    "query": "SELECT NBASTIDOR FROM (SELECT DISTINCT NBASTIDOR, MAX(fecha_creacion) as max_f FROM LOG_TABLA GROUP BY NBASTIDOR) AS t ORDER BY max_f DESC",
                    "refresh": 1,
                    "regex": "",
                    "skipUrlSync": False,
                    "sort": 0,
                    "type": "query"
                }
            ]
        },
        "time": {
            "from": "now-30d",
            "to": "now"
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "1d"
            ]
        },
        "timezone": "",
        "title": "LOGISNEXT — DISTRIBUIDOR",
        "uid": DASHBOARD_UID,
        "version": existing.get("version", 1) + 1
    }

    # Save to local file
    with open('grafana/provisioning/dashboards/distribuidor_dashboard.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    print("[OK] Saved local JSON file to grafana/provisioning/dashboards/distribuidor_dashboard.json")

    # Push to Grafana API
    creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASS}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    
    payload = {
        "dashboard": dashboard,
        "folderId": 13, # Folder "Logisnext MES" has id 13
        "overwrite": True,
        "message": "Agrupamiento de gauges dentro de la misma ventana"
    }
    
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"[OK] Dashboard successfully pushed to Grafana API! Status: {res.get('status')}, Version: {res.get('version')}")
    except urllib.error.HTTPError as e:
        print(f"ERROR pushing dashboard: {e.code} - {e.read().decode()}")
        sys.exit(1)

if __name__ == '__main__':
    main()
