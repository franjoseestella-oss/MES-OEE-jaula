import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Let's find all table names in DAFEED
    print("--- TABLES IN DATABASE ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tables = [row[0] for row in cursor.fetchall()]
    print(tables)
    
    # If there is a calendar table, let's check it
    calendar_table = None
    for t in tables:
        if "calendario" in t.lower() or "calendar" in t.lower() or "calen" in t.lower():
            calendar_table = t
            break
            
    if calendar_table:
        print(f"\n--- CALENDAR TABLE found: {calendar_table} ---")
        cursor.execute(f"SELECT TOP 20 * FROM {calendar_table}")
        columns = [column[0] for column in cursor.description]
        print("Columns:", columns)
        for row in cursor.fetchall():
            print(row)
            
        print("\n--- CALENDAR FOR JUNE 2026 ---")
        # Let's query June 2026 from calendar
        # We need to see if columns contain date/fecha
        date_col = None
        for c in columns:
            if "fecha" in c.lower() or "date" in c.lower():
                date_col = c
                break
        if date_col:
            cursor.execute(f"SELECT * FROM {calendar_table} WHERE {date_col} LIKE '2026-06-%' OR {date_col} LIKE '202606%' ORDER BY {date_col}")
            for row in cursor.fetchall():
                print(row)
    else:
        print("\nNo calendar table found.")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
