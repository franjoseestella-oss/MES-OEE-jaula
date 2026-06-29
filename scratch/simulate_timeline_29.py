import pyodbc
import dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
dotenv.load_dotenv()

host = os.getenv("SQL_SERVER_HOST", "DESKTOP-PMRMSPT\\SQLEXPRESS")
database = os.getenv("SQL_SERVER_DATABASE", "DAFEED")
user = os.getenv("SQL_SERVER_USER", "usuario_readonly")
password = os.getenv("SQL_SERVER_PASSWORD", "Logisnext2026!")
driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")

conn_str = f"DRIVER={{{driver}}};SERVER={host};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    with open("scratch/panel_10_sql.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    sql_run = sql.replace("$__timeFrom()", "'2026-06-29T07:00:00Z'")
    
    print("Running timeline query simulation for 2026-06-29...")
    cursor.execute("SET NOCOUNT ON;\n" + sql_run)
    rows = cursor.fetchall()
    
    print(f"Returned {len(rows)} rows.")
    current_metric = None
    for r in rows:
        metric = r[1]
        time = r[0]
        val = r[2]
        if metric != current_metric:
            print(f"\n--- Sequence: {metric.replace(chr(10), ' - ')} ---")
            current_metric = metric
        print(f"  {time} -> {val}")
        
    conn.close()
except Exception as e:
    print("Error:", e)
