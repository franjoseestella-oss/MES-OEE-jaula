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

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

raw_sql = ""
for p in dash.get("panels", []):
    if p.get("id") == 10:
        raw_sql = p["targets"][0]["rawSql"]
        break

# Replaced time parameter to 2026-06-29
sql_to_run = "SET NOCOUNT ON;\n" + raw_sql.replace("$__timeFrom()", "'2026-06-29 00:00:00'").replace("$__timeTo()", "'2026-06-29 23:59:59'")

print("--- RUNNING PANEL 10 QUERY AND PRINTING DETAILED ROWS FOR 0261 ---")
try:
    cursor.execute(sql_to_run)
    rows = cursor.fetchall()
    # Print column names
    col_names = [col[0] for col in cursor.description]
    print(f"Columns: {col_names}")
    for r in rows:
        metric = r[1]
        if "0261" in metric:
            print(f"time: {r[0]}, metric: {r[1]}, value: {r[2]}")
except Exception as e:
    print(f"Error running query: {e}")

conn.close()
