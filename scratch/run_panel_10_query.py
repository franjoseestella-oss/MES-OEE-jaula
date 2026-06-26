import pyodbc
import sys

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
    print(f"Error connecting to database via Windows Auth: {e}")
    sys.exit(1)

import json
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

# Add SET NOCOUNT ON; and replace time parameters
sql_to_run = "SET NOCOUNT ON;\n" + raw_sql.replace("$__timeFrom()", "'2026-06-26 00:00:00'").replace("$__timeTo()", "'2026-06-26 23:59:59'")

print("\n--- RUNNING PANEL 10 QUERY FOR 2026-06-26 ---")
try:
    cursor.execute(sql_to_run)
    rows = cursor.fetchall()
    print(f"Returned {len(rows)} rows. Showing first 100 rows:")
    for r in rows[:100]:
        print(f"time: {r[0]}, metric: {r[1]}, value: {r[2]}")
except Exception as e:
    print(f"Error running query: {e}")

conn.close()
