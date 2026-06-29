import pyodbc
import sys
import json
import re

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

modified_sql = raw_sql

# 1. Replace the filter condition occurrences
# Let's use regex to handle any potential whitespace differences
filter_pattern = r"s\.actual_start\s+IS\s+NOT\s+NULL\s+AND\s+\(\s*s\.actual_start\s*<\s*s\.planned_start\s+OR\s+s\.actual_start\s*>=\s*s\.planned_end\s*\)\s+THEN\s+s\.actual_start\s*"
modified_sql, count = re.subn(filter_pattern, "s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start ", modified_sql)
print(f"Replaced {count} occurrences of filter condition.")

# 2. Add the gap check in the SELECT CASE expression:
target_marker = "END THEN NULL"
new_gap_check = "\n            WHEN s.actual_start IS NOT NULL AND s.actual_start >= s.planned_end AND ft.t >= s.planned_end AND ft.t < s.actual_start THEN NULL"
modified_sql = modified_sql.replace(target_marker, target_marker + new_gap_check)
print("Added gap check after 'END THEN NULL'")

# 3. Modify the alarm recovery check to only apply before s.actual_start:
# Let's search for the pattern and replace it using regex
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

modified_sql, count = re.subn(alarm_pattern, replacement, modified_sql)
print(f"Replaced {count} occurrences of alarm recovery check.")

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
