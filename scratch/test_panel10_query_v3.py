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
    
    # 1. Update lower bound filter
    old_where = "WHERE bt.t >= s.planned_start"
    new_where = """WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
    query = query.replace(old_where, new_where)
    
    # 2. Update value case for early start to be 'Exceso de tiempo' (grey)
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
    
    # 3. Mock active sequence to be SFB08E704694 starting at 13:34 local time (11:34:00 UTC)
    # We locate the SELECT TOP 1 for active cycle and mock it:
    old_select_active = """SELECT TOP 1 
    @ActiveBastidor = NBASTIDOR,
    @ActiveStartDT = DATEADD(hour, -@UTCOffset, TRY_CONVERT(DATETIME, 
        SUBSTRING(FECHA_INICIO_CICLO, 13, 4) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 10, 2) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 7, 2) + 'T' + 
        SUBSTRING(FECHA_INICIO_CICLO, 1, 5) + ':00'
    ))
FROM dbo.REFERENCIA_EN_CICLO
WHERE LEN(FECHA_INICIO_CICLO) >= 16;"""

    new_select_active = """SET @ActiveBastidor = 'SFB08E704694';
SET @ActiveStartDT = '2026-06-25T11:34:00Z';"""

    query = query.replace(old_select_active, new_select_active)
    
    query_replaced = query.replace("$__timeFrom()", "'2026-06-25T00:00:00Z'")
    query_replaced = "SET NOCOUNT ON;\n" + query_replaced
    
    cursor.execute(query_replaced)
    rows = cursor.fetchall()
    
    print("\nMocked Time | Metric | Value")
    print("-" * 50)
    for r in rows:
        if "0288" in r[1] or "0289" in r[1]:
            print(f"{r[0]} | {r[1].replace(chr(10), ' ')} | {r[2]}")
            
except Exception as e:
    print("Error:", e)
