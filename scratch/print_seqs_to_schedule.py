import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    with open("scratch/panel10_query_full.sql", "r", encoding="utf-8") as f:
        query = f.read()
    
    # We want to print #SeqsToSchedule content before the final select
    # Let's truncate the query at BoundedTimestamps and print #SeqsToSchedule
    idx = query.find("WITH AlarmIntervals")
    part_query = query[:idx]
    part_query += "\nSELECT id, secuencia, bastidor, planned_start, planned_end, actual_start, actual_end FROM #SeqsToSchedule ORDER BY id;"
    
    part_query = part_query.replace("$__timeFrom()", "'2026-06-25T00:00:00Z'")
    part_query = "SET NOCOUNT ON;\n" + part_query
    
    cursor.execute(part_query)
    rows = cursor.fetchall()
    print("Seqs to Schedule for today (2026-06-25):")
    print("-" * 100)
    for r in rows:
        print(f"ID: {r[0]} | Seq: {r[1]} | Bastidor: {r[2]} | Planned: {r[3]} to {r[4]} | Actual: {r[5]} to {r[6]}")
        
except Exception as e:
    print("Error:", e)
