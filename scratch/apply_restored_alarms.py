import json
import os

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

target_found = False
for panel in dashboard_data.get("panels", []):
    if panel.get("id") == 10:
        targets = panel.get("targets", [])
        if targets:
            raw_sql = targets[0].get("rawSql", "")
            
            # The exact part of the query to replace
            old_segment = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'
            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN"""
            
            new_segment = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end
                 ) THEN 'Alarma'
            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'
            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN"""

            if old_segment in raw_sql:
                new_raw_sql = raw_sql.replace(old_segment, new_segment)
                targets[0]["rawSql"] = new_raw_sql
                target_found = True
                print("Target segment found and replaced successfully!")
            else:
                # Let's try replacing with a normalized version of line endings if needed
                normalized_raw = raw_sql.replace("\r\n", "\n")
                normalized_old = old_segment.replace("\r\n", "\n")
                normalized_new = new_segment.replace("\r\n", "\n")
                if normalized_old in normalized_raw:
                    targets[0]["rawSql"] = normalized_raw.replace(normalized_old, normalized_new)
                    target_found = True
                    print("Target segment found and replaced successfully (normalized line endings)!")
                else:
                    print("Error: Could not find the old query segment in rawSql.")

if target_found:
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    print("Updated plan_dashboard.json successfully.")
else:
    print("Failed to update plan_dashboard.json.")
