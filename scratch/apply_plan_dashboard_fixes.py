import json
import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

dashboard_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    dash = json.load(f)

# Find Panel 10
panel_found = False
for p in dash.get("panels", []):
    if p.get("id") == 10:
        panel_found = True
        raw_sql = p["targets"][0]["rawSql"]
        
        modified_sql = raw_sql

        # 1. Replace the filter condition occurrences
        filter_pattern = r"s\.actual_start\s+IS\s+NOT\s+NULL\s+AND\s+\(\s*s\.actual_start\s*<\s*s\.planned_start\s+OR\s+s\.actual_start\s*>=\s*s\.planned_end\s*\)\s+THEN\s+s\.actual_start\s*"
        modified_sql, count_filter = re.subn(filter_pattern, "s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start ", modified_sql)
        print(f"Replaced {count_filter} occurrences of filter condition.")

        # 2. Add the gap check in the SELECT CASE expression:
        target_marker = "END THEN NULL"
        new_gap_check = "\n            WHEN s.actual_start IS NOT NULL AND s.actual_start >= s.planned_end AND ft.t >= s.planned_end AND ft.t < s.actual_start THEN NULL"
        
        # Verify if target_marker exists exactly once to prevent double addition
        if modified_sql.count(target_marker) == 1:
            modified_sql = modified_sql.replace(target_marker, target_marker + new_gap_check)
            print("Added gap check after 'END THEN NULL'")
        else:
            print("WARNING: 'END THEN NULL' does not occur exactly once. Check if already modified.")

        # 3. Modify the alarm recovery check to only apply before s.actual_start:
        alarm_pattern = (
            r"WHEN\s+s\.slot_idx\s*=\s*COALESCE\(@ActiveSlotIdx,\s*@TheoreticalActiveSlotIdx\)\s*\n?\s*"
            r"AND\s+EXISTS\s*\(\s*\n?\s*"
            r"SELECT\s+1\s+FROM\s+AlarmIntervals\s+a\s*\n?\s*"
            r"WHERE\s+ft\.t\s*>=\s*a\.alarm_end\s*\n?\s*"
            r"AND\s+a\.alarm_end\s*>=\s*CASE\s*\n?\s*"
            r"WHEN\s+s\.actual_start\s+IS\s+NOT\s+NULL\s+AND\s+s\.actual_start\s*<\s*s\.planned_start\s+THEN\s+s\.actual_start\s*\n?\s*"
            r"ELSE\s+s\.planned_start\s*\n?\s*"
            r"END\s*\n?\s*"
            r"\)\s+THEN\s+'Esperando máquina'"
        )

        replacement = (
            "WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)\n"
            "                 AND (s.actual_start IS NULL OR ft.t < s.actual_start)\n"
            "                 AND EXISTS (\n"
            "                     SELECT 1 FROM AlarmIntervals a \n"
            "                     WHERE ft.t >= a.alarm_end\n"
            "                       AND a.alarm_end >= CASE \n"
            "                                            WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start \n"
            "                                            ELSE s.planned_start \n"
            "                                          END\n"
            "                 ) THEN 'Esperando máquina'"
        )

        modified_sql, count_alarm = re.subn(alarm_pattern, replacement, modified_sql)
        print(f"Replaced {count_alarm} occurrences of alarm recovery check.")

        # Update the panel's rawSql
        p["targets"][0]["rawSql"] = modified_sql
        break

if not panel_found:
    print("Could not find Panel 10 in dashboard JSON.")
    sys.exit(1)

# Write the modified JSON back
with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(dash, f, indent=4, ensure_ascii=False)

print("Successfully saved modifications to plan_dashboard.json!")
