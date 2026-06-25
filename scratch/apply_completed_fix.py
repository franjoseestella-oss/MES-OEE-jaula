import json

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Locate Panel 10
panel_10 = None
for panel in db.get("panels", []):
    if panel.get("id") == 10:
        panel_10 = panel
        break

if panel_10:
    target = panel_10.get("targets", [])[0]
    sql = target.get("rawSql")
    
    old_clause = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx THEN"
    new_clause = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL THEN"
    
    if old_clause in sql:
        sql = sql.replace(old_clause, new_clause)
        target["rawSql"] = sql
        print("Successfully updated SQL query in plan_dashboard.json.")
    else:
        print("Warning: Could not find target pattern in SQL query inside plan_dashboard.json.")
        
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
else:
    print("Error: Panel 10 not found in plan_dashboard.json.")

# Also update scratch/panel10_query_full.sql
sql_file = "scratch/panel10_query_full.sql"
try:
    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if old_clause in content:
        content = content.replace(old_clause, new_clause)
        print("Updated scratch/panel10_query_full.sql.")
    else:
        print("Warning: Could not find target pattern in scratch/panel10_query_full.sql.")
        
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(content)
except Exception as e:
    print("Error updating panel10_query_full.sql:", e)
