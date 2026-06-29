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
    
    # We will simulate the part of the query that populates #SeqsToSchedule and print it
    with open("scratch/panel_10_sql.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    # We only want to run up to the creation of #SeqsToSchedule
    # Let's find where SELECT FROM #SeqsToSchedule is, or we can just append a SELECT at the end
    debug_sql = sql.replace("$__timeFrom()", "'2026-06-29T07:00:00Z'")
    
    # Let's drop #CalendarSlots, #MappedSeqs, #SeqsToSchedule if exist
    # and then print them
    cursor.execute("""
    SET NOCOUNT ON;
    """ + debug_sql + """
    SELECT id, secuencia, bastidor, planned_start, planned_end, actual_start, actual_end 
    FROM #SeqsToSchedule 
    ORDER BY slot_idx;
    """)
    
    rows = cursor.fetchall()
    print("--- SeqsToSchedule for 2026-06-29 ---")
    for r in rows:
        print(r)
        
    conn.close()
except Exception as e:
    print("Error:", e)
