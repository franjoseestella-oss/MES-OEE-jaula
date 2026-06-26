import json
import subprocess
import os

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Panel 10 query with LOG_ALARMAS duration-interval integration, active-slot blocking, and current-time capping
with open("scratch/panel10_query_full.sql", "r", encoding="utf-8") as f:
    panel_10_query = f.read()

updated = 0
for p in db.get("panels", []):
    if p.get("id") == 10:
        # Update rawSql
        p["targets"][0]["rawSql"] = panel_10_query
        
        # Update value mappings options to include "Exceso de tiempo" and "Alarma"
        mappings = p.setdefault("fieldConfig", {}).setdefault("defaults", {}).setdefault("mappings", [])
        if mappings and len(mappings) > 0 and mappings[0].get("type") == "value":
            opts = mappings[0].get("options", {})
            opts["Exceso de tiempo"] = {
                "color": "#5F6B7C",
                "index": 6,
                "text": "Exceso de tiempo"
            }
            opts["Alarma"] = {
                "color": "#E32636",
                "index": 7,
                "text": "Alarma"
            }
        
        updated += 1

if updated == 1:
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Successfully updated Panel 10 query with finalized Alarm, unprocessed and progress-cap logic.")
else:
    print(f"Error: Panel 10 not found.")
