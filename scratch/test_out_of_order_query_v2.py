import pyodbc
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

raw_sql = ""
for p in dash.get("panels", []):
    if p.get("id") == 10:
        raw_sql = p["targets"][0]["rawSql"]
        break

if not raw_sql:
    print("Could not find Panel 10 rawSql")
    sys.exit(1)

# Apply our proposed changes to raw_sql
modified_sql = raw_sql

# 1. Replace the condition in FilteredTimestamps:
old_filter_cond = "s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start"
new_filter_cond = "s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start"
modified_sql = modified_sql.replace(old_filter_cond, new_filter_cond)

# 2. Add the gap check in the SELECT CASE expression:
# We want to insert:
# "WHEN s.actual_start IS NOT NULL AND s.actual_start >= s.planned_end AND ft.t >= s.planned_end AND ft.t < s.actual_start THEN NULL"
# right after the first WHEN block (which ends with "END THEN NULL")

target_marker = "END THEN NULL"
new_gap_check = "\n            WHEN s.actual_start IS NOT NULL AND s.actual_start >= s.planned_end AND ft.t >= s.planned_end AND ft.t < s.actual_start THEN NULL"
modified_sql = modified_sql.replace(target_marker, target_marker + new_gap_check)

# 3. Modify the alarm recovery check to only apply before s.actual_start:
old_alarm_recovery = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'"""

new_alarm_recovery = """            WHEN s.slot_idx = COALESCE(@ActiveSlotIdx, @TheoreticalActiveSlotIdx)
                 AND (s.actual_start IS NULL OR ft.t < s.actual_start)
                 AND EXISTS (
                     SELECT 1 FROM AlarmIntervals a 
                     WHERE ft.t >= a.alarm_end
                       AND a.alarm_end >= CASE 
                                            WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                                            ELSE s.planned_start 
                                          END
                 ) THEN 'Esperando máquina'"""

if old_alarm_recovery in modified_sql:
    print("Found alarm recovery check, replacing...")
    modified_sql = modified_sql.replace(old_alarm_recovery, new_alarm_recovery)
else:
    # Try with different whitespace normalization just in case
    # Since we can do a raw replace if we verify it, let's see.
    # Let's print if replacement succeeded.
    pass

# Run query for 2026-06-29
sql_to_run = "SET NOCOUNT ON;\n" + modified_sql.replace("$__timeFrom()", "'2026-06-29 00:00:00'").replace("$__timeTo()", "'2026-06-29 23:59:59'")

print("\n--- RUNNING REVISED PANEL 10 QUERY FOR 2026-06-29 ---")
try:
    cursor.execute(sql_to_run)
    rows = cursor.fetchall()
    print(f"Returned {len(rows)} rows. Showing rows for 0261:")
    for r in rows:
        if "0261" in r[1]:
            print(f"time: {r[0]}, metric: {r[1].replace(chr(10), ' ')}, value: {r[2]}")
except Exception as e:
    print(f"Error running query: {e}")

conn.close()
