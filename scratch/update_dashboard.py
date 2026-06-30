import json
import os

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    d = json.load(f)

found = False
for p in d.get("panels", []):
    if p.get("id") == 10:
        targets = p.get("targets", [])
        if targets:
            raw_sql = targets[0].get("rawSql", "")
            print("Found rawSql in Panel 10.")
            
            # Find the two occurrences of s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
            # and replace them with the dynamic active slot subquery.
            old_str_1 = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'"""
                 
            new_str_1 = """            WHEN s.slot_idx = COALESCE(
                     (SELECT MIN(slot_idx) FROM #SeqsToSchedule WHERE actual_start IS NOT NULL AND actual_start <= ft.t AND (actual_end IS NULL OR actual_end > ft.t)),
                     (SELECT TOP 1 slot_idx FROM #SeqsToSchedule WHERE planned_start <= ft.t AND planned_end >= ft.t),
                     (SELECT MAX(slot_idx) FROM #SeqsToSchedule WHERE planned_start <= ft.t),
                     1
                 )
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'"""

            old_str_2 = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND (s.actual_start IS NULL OR ft.t < s.actual_start)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'"""
                 
            new_str_2 = """            WHEN s.slot_idx = COALESCE(
                     (SELECT MIN(slot_idx) FROM #SeqsToSchedule WHERE actual_start IS NOT NULL AND actual_start <= ft.t AND (actual_end IS NULL OR actual_end > ft.t)),
                     (SELECT TOP 1 slot_idx FROM #SeqsToSchedule WHERE planned_start <= ft.t AND planned_end >= ft.t),
                     (SELECT MAX(slot_idx) FROM #SeqsToSchedule WHERE planned_start <= ft.t),
                     1
                 )
                 AND (s.actual_start IS NULL OR ft.t < s.actual_start)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'"""

            # To be absolutely sure, we do a flexible replace or a direct replace handling carriage returns.
            # Normalize line endings in raw_sql and the replacement strings to \n
            raw_sql_norm = raw_sql.replace("\r\n", "\n")
            old_str_1_norm = old_str_1.replace("\r\n", "\n")
            new_str_1_norm = new_str_1.replace("\r\n", "\n")
            old_str_2_norm = old_str_2.replace("\r\n", "\n")
            new_str_2_norm = new_str_2.replace("\r\n", "\n")
            
            if old_str_1_norm in raw_sql_norm:
                print("Matches old_str_1!")
            else:
                print("Does not match old_str_1 exactly, checking parts...")
                
            if old_str_2_norm in raw_sql_norm:
                print("Matches old_str_2!")
            else:
                print("Does not match old_str_2 exactly, checking parts...")

            # Let's perform the replacement
            updated_sql = raw_sql_norm.replace(old_str_1_norm, new_str_1_norm)
            updated_sql = updated_sql.replace(old_str_2_norm, new_str_2_norm)
            
            # Put back in the target
            targets[0]["rawSql"] = updated_sql
            found = True

if found:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("Successfully updated plan_dashboard.json!")
else:
    print("Could not find Panel 10 or apply updates.")
