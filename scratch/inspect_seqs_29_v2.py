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
        
    # We want to stop before the final SELECT and instead select directly from #SeqsToSchedule
    pos = sql.find("SELECT time, metric, value FROM (")
    if pos == -1:
        print("Could not find final SELECT")
        sys.exit(1)
        
    first_part = sql[:pos]
    
    debug_sql = first_part + """
    SELECT id, slot_idx, secuencia, bastidor, planned_start, planned_end, actual_start, actual_end 
    FROM #SeqsToSchedule 
    ORDER BY slot_idx;
    """
    
    debug_sql = debug_sql.replace("$__timeFrom()", "'2026-06-29T07:00:00Z'")
    
    cursor.execute("SET NOCOUNT ON;\n" + debug_sql)
    rows = cursor.fetchall()
    print("--- SeqsToSchedule for 2026-06-29 ---")
    for r in rows:
        print(f"ID: {r[0]} | Slot: {r[1]} | Seq: {r[2]} | Bast: {r[3]} | P_Start: {r[4]} | P_End: {r[5]} | A_Start: {r[6]} | A_End: {r[7]}")
        
    conn.close()
except Exception as e:
    print("Error:", e)
