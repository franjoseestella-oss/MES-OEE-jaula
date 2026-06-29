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

# Replace the condition in FilteredTimestamps:
# WHERE bt.t >= CASE WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start ELSE s.planned_start END
old_filter_cond = "s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start"
new_filter_cond = "s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start"

if old_filter_cond in modified_sql:
    print("Found FilteredTimestamps condition, replacing...")
    modified_sql = modified_sql.replace(old_filter_cond, new_filter_cond)
else:
    print("WARNING: FilteredTimestamps condition not found exactly in rawSql")

# Replace in AlarmIntervals end condition if any:
# a.alarm_end >= CASE WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start ELSE s.planned_start END
if old_filter_cond in modified_sql:
    # Since we did a replace, it might have already replaced both. Let's verify by printing how many occurrences are left.
    pass

# Run query for 2026-06-29
sql_to_run = "SET NOCOUNT ON;\n" + modified_sql.replace("$__timeFrom()", "'2026-06-29 00:00:00'").replace("$__timeTo()", "'2026-06-29 23:59:59'")

print("\n--- RUNNING MODIFIED PANEL 10 QUERY FOR 2026-06-29 ---")
try:
    cursor.execute(sql_to_run)
    rows = cursor.fetchall()
    print(f"Returned {len(rows)} rows. Showing rows for 0261:")
    for r in rows:
        if "0261" in r[1]:
            print(f"time: {r[0]}, metric: {r[1]}, value: {r[2]}")
except Exception as e:
    print(f"Error running query: {e}")

conn.close()
