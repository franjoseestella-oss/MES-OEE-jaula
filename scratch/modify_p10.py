import json

path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

modified = False
for p in db.get("panels", []):
    if p.get("id") == 10:
        for t in p.get("targets", []):
            if "rawSql" in t:
                sql = t["rawSql"]
                target_str = """            WHEN EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'"""
                 
                replacement_str = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'"""
                
                # Let's normalize newlines to make sure search works
                if target_str in sql:
                    sql = sql.replace(target_str, replacement_str)
                    t["rawSql"] = sql
                    modified = True
                elif target_str.replace("\n", "\r\n") in sql:
                    sql = sql.replace(target_str.replace("\n", "\r\n"), replacement_str.replace("\n", "\r\n"))
                    t["rawSql"] = sql
                    modified = True
                else:
                    # Let's try replacing with standard whitespace normalization
                    print("Exact string not found. Trying flexible match...")
                    import re
                    pattern = re.compile(
                        r"WHEN\s+EXISTS\s*\(\s*SELECT\s+1\s+FROM\s+AlarmIntervals\s+a\s+WHERE\s+ft\.t\s*>=\s*a\.alarm_start\s+AND\s+ft\.t\s*<\s*a\.alarm_end\s*\)\s+THEN\s+'Alarma'",
                        re.IGNORECASE
                    )
                    sql, count = pattern.subn(
                        "WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)\n                 AND EXISTS (\n                     SELECT 1 FROM AlarmIntervals a \n                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end\n                 ) THEN 'Alarma'",
                        sql
                    )
                    if count > 0:
                        t["rawSql"] = sql
                        modified = True
                        print(f"Replaced using regex. Count: {count}")

if modified:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Successfully modified plan_dashboard.json!")
else:
    print("Warning: No changes made. Target query pattern not found.")
