import pyodbc
import json
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
    print(f"Error connecting to database: {e}")
    sys.exit(1)

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 4:
        for t in p.get("targets", []):
            ref = t.get("refId")
            raw_sql = t.get("rawSql")
            sql_to_run = "SET NOCOUNT ON;\n" + raw_sql.replace("$__timeFrom()", "'2026-06-22 00:00:00'").replace("$__timeTo()", "'2026-06-22 23:59:59'")
            print(f"\n--- RUNNING PANEL 4 TARGET {ref} FOR 2026-06-22 ---")
            try:
                cursor.execute(sql_to_run)
                rows = cursor.fetchall()
                print(f"Returned {len(rows)} rows. Showing first 10 rows:")
                for r in rows[:10]:
                    print(f"time: {r[0]}, value: {r[1]}")
            except Exception as e:
                print(f"Error: {e}")

conn.close()
