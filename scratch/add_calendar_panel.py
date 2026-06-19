import json

plan_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(plan_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Check if panel 7 already exists to avoid duplicate
panels = db.get("panels", [])
panel_ids = [p.get("id") for p in panels]

if 7 in panel_ids:
    print("Panel 7 already exists. Removing it first for clean update.")
    panels = [p for p in panels if p.get("id") != 7]

new_panel = {
  "datasource": {
    "uid": "mes_sqlserver"
  },
  "fieldConfig": {
    "defaults": {
      "custom": {
        "align": "auto",
        "displayMode": "auto",
        "inspect": False
      },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {
            "color": "green",
            "value": None
          }
        ]
      }
    },
    "overrides": [
      {
        "matcher": {
          "id": "byName",
          "options": "Laborable"
        },
        "properties": [
          {
            "id": "mappings",
            "value": [
              {
                "options": {
                  "No": {
                    "color": "red",
                    "index": 1,
                    "text": "No"
                  },
                  "Sí": {
                    "color": "green",
                    "index": 0,
                    "text": "Sí"
                  }
                },
                "type": "value"
              }
            ]
          },
          {
            "id": "custom.cellOptions",
            "value": {
              "type": "color-background"
            }
          }
        ]
      }
    ]
  },
  "gridPos": {
    "h": 10,
    "w": 24,
    "x": 0,
    "y": 25
  },
  "id": 7,
  "options": {
    "cellHeight": "sm",
    "footer": {
      "countRows": False,
      "fields": "",
      "reducer": [
        "sum"
      ],
      "show": False
    },
    "showHeader": True,
    "sortBy": []
  },
  "pluginVersion": "10.4.2",
  "targets": [
    {
      "datasource": {
        "type": "mssql",
        "uid": "mes_sqlserver"
      },
      "editorMode": "code",
      "format": "table",
      "rawQuery": True,
      "rawSql": "SELECT\n  COALESCE(CONVERT(varchar(10), TRY_CAST(Fecha AS DATE), 103), '') AS [Fecha],\n  Tipo_Dia AS [Tipo de Día],\n  CASE WHEN Laborable = 1 THEN 'Sí' ELSE 'No' END AS [Laborable],\n  Cant_A_Fabricar AS [Unidades a Fabricar]\nFROM dbo.CALENDARIO_LABORAL\nWHERE $__timeFilter(Fecha)\nORDER BY Fecha ASC",
      "refId": "A"
    }
  ],
  "title": "📅 CALENDARIO LABORAL Y PLANIFICACIÓN DE UNIDADES",
  "type": "table"
}

panels.append(new_panel)
db["panels"] = panels

with open(plan_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully added CALENDARIO LABORAL table panel to plan_dashboard.json")
