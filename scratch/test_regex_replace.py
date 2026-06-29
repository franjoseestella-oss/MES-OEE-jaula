import json
import re

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

raw_sql = ""
for p in dash.get("panels", []):
    if p.get("id") == 10:
        raw_sql = p["targets"][0]["rawSql"]
        break

if not raw_sql:
    print("Could not find Panel 10 query")
    import sys; sys.exit(1)

# Let's inspect all occurrences of:
# s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start
matches = list(re.finditer(r"s\.actual_start\s+IS\s+NOT\s+NULL\s+AND\s+\(\s*s\.actual_start\s*<\s*s\.planned_start\s+OR\s+s\.actual_start\s*>=\s*s\.planned_end\s*\)\s+THEN\s+s\.actual_start", raw_sql))
print(f"Found {len(matches)} occurrences of filter condition")

# Let's see the alarm recovery block:
# WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
# AND EXISTS ( SELECT 1 FROM AlarmIntervals a WHERE ft.t >= a.alarm_end AND a.alarm_end >= CASE ... END ) THEN 'Esperando máquina'
# We want to replace this block.
# Let's find it.
alarm_recovery_pattern = r"(WHEN\s+s\.slot_idx\s*=\s*COALESCE\(@ActiveSlotIdx,\s*@TheoreticalActiveSlotIdx\)\s*\n?\s*AND\s+EXISTS\s*\(\s*\n?\s*SELECT\s+1\s+FROM\s+AlarmIntervals\s+a\s*\n?\s*WHERE\s+ft\.t\s*>=\s*a\.alarm_end\s*\n?\s*AND\s+a\.alarm_end\s*>=\s*CASE\s*\n?\s*WHEN\s+s\.actual_start\s+IS\s+NOT\s+NULL\s+AND\s+\(\s*s\.actual_start\s*<\s*s\.planned_start\s+OR\s+s\.actual_start\s*>=\s*s\.planned_end\s*\)\s+THEN\s+s\.actual_start\s*\n?\s*ELSE\s+s\.planned_start\s*\n?\s*END\s*\n?\s*\)\s+THEN\s+'Esperando máquina')"

match_recovery = re.search(alarm_recovery_pattern, raw_sql)
if match_recovery:
    print("Found alarm recovery block!")
else:
    print("Could not find alarm recovery block via regex")
