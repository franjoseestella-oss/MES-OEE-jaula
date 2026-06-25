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
    
    # Apply our fix to the lower bound filter in FilteredTimestamps
    old_where = "WHERE bt.t >= s.planned_start"
    new_where = """WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
    
    if old_where in query:
        query_fixed = query.replace(old_where, new_where)
        print("Replaced lower bound filter in test query.")
    else:
        print("Error: Could not find target where clause in query.")
        query_fixed = query
        
    query_replaced = query_fixed.replace("$__timeFrom()", "'2026-06-25T00:00:00Z'")
    query_replaced = "SET NOCOUNT ON;\n" + query_replaced
    
    cursor.execute(query_replaced)
    rows = cursor.fetchall()
    
    print("\nTime | Metric | Value")
    print("-" * 50)
    for r in rows:
        if "0288" in r[1] or "0289" in r[1]:
            print(f"{r[0]} | {r[1].replace(chr(10), ' ')} | {r[2]}")
            
except Exception as e:
    print("Error:", e)
