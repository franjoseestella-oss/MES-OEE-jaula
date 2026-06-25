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
    
    old_phrase = """    WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
                  
    new_phrase = """    WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
                  
    if old_phrase in sql:
        sql = sql.replace(old_phrase, new_phrase)
        target["rawSql"] = sql
        print("Successfully updated SQL query in plan_dashboard.json.")
    else:
        # Let's try direct substring replacement if whitespace differs slightly
        old_normalized = "s.actual_start < s.planned_start THEN s.actual_start"
        new_normalized = "(s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start"
        if old_normalized in sql:
            sql = sql.replace(old_normalized, new_normalized)
            target["rawSql"] = sql
            print("Successfully updated SQL query (normalized replacement) in plan_dashboard.json.")
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
    
    # In the file, the line might still be "WHERE bt.t >= s.planned_start" or the case statement depending on what was saved
    if "WHERE bt.t >= s.planned_start" in content:
        content = content.replace("WHERE bt.t >= s.planned_start", """WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start 
                      ELSE s.planned_start 
                  END""")
        print("Updated scratch/panel10_query_full.sql from simple planned_start check.")
    elif "s.actual_start < s.planned_start THEN s.actual_start" in content:
        content = content.replace("s.actual_start < s.planned_start THEN s.actual_start", "(s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start")
        print("Updated scratch/panel10_query_full.sql (case check).")
        
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(content)
except Exception as e:
    print("Error updating panel10_query_full.sql:", e)
