import json
import os

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION%s" % (
    r"MES-OEE\grafana\provisioning\dashboards\distribuidor_dashboard.json"
)

# Fix up the path in case we want to be safe
dashboard_path = os.path.abspath(r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\distribuidor_dashboard.json")

print(f"Reading from: {dashboard_path}")
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

target_panel_ids = [102, 104, 106, 111, 113, 115]

for panel in dashboard.get("panels", []):
    pid = panel.get("id")
    if pid in target_panel_ids:
        print(f"Updating Panel {pid}: {panel.get('title')}")
        
        # 1. Update min and max statically
        if "fieldConfig" not in panel:
            panel["fieldConfig"] = {}
        if "defaults" not in panel["fieldConfig"]:
            panel["fieldConfig"]["defaults"] = {}
            
        panel["fieldConfig"]["defaults"]["min"] = 0
        panel["fieldConfig"]["defaults"]["max"] = 100
        
        # 2. Update thresholds structure
        panel["fieldConfig"]["defaults"]["thresholds"] = {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636"}, # base: Red
                {"color": "#2FD06A", "value": 0}, # step 1: Green placeholder for min_pct
                {"color": "#E32636", "value": 100} # step 2: Red placeholder for max_pct
            ]
        }
        
        # 3. Update SQL query
        for target in panel.get("targets", []):
            if "rawSql" in target:
                sql = target["rawSql"]
                sql = sql.replace("${min_pct} AS [min]", "${min_pct} AS [threshold_min]")
                sql = sql.replace("${max_pct} AS [max]", "${max_pct} AS [threshold_max]")
                target["rawSql"] = sql
                
        # 4. Update transformations
        panel["transformations"] = [
            {
                "id": "configFromData",
                "options": {
                    "configRefId": "A",
                    "mappings": [
                        {
                            "fieldName": "threshold_min",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#2FD06A"
                                }
                            },
                            "handlerKey": "threshold1"
                        },
                        {
                            "fieldName": "threshold_max",
                            "handlerArguments": {
                                "threshold": {
                                    "color": "#E32636"
                                }
                            },
                            "handlerKey": "threshold1"
                        }
                    ]
                }
            }
        ]

with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print("Finished updating dashboard json file.")
