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
    
    # Let's apply our current modifications (v154 query state)
    old_where = "WHERE bt.t >= s.planned_start"
    new_where = """WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
    query = query.replace(old_where, new_where)
    
    old_case = """            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN
                CASE 
                    WHEN ft.t >= s.planned_end THEN 'Exceso de tiempo'
                    ELSE 'En proceso'
                END"""
                
    new_case = """            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN
                CASE 
                    WHEN ft.t < s.planned_start OR ft.t >= s.planned_end THEN 'Exceso de tiempo'
                    ELSE 'En proceso'
                END"""
    query = query.replace(old_case, new_case)
    
    query_replaced = query.replace("$__timeFrom()", "'2026-06-25T00:00:00Z'")
    query_replaced = "SET NOCOUNT ON;\n" + query_replaced
    
    cursor.execute(query_replaced)
    rows = cursor.fetchall()
    
    print("\nTime | Metric | Value")
    print("-" * 50)
    for r in rows:
        if "0271" in r[1] or "0272" in r[1] or "0273" in r[1]:
            print(f"{r[0]} | {r[1].replace(chr(10), ' ')} | {r[2]}")
            
except Exception as e:
    print("Error:", e)
