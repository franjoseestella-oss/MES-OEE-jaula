import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # 1. check if LOG_ALARMAS table exists
    cursor.execute("""
        SELECT name FROM sys.tables WHERE name = 'LOG_ALARMAS'
    """)
    res = cursor.fetchone()
    print("Table LOG_ALARMAS exists:", res is not None)
    
    if res:
        # 2. Get columns of LOG_ALARMAS
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'LOG_ALARMAS'")
        cols = cursor.fetchall()
        print("Columns in LOG_ALARMAS:")
        for col in cols:
            print(f"  {col[0]} ({col[1]})")
            
        # 3. Get first 10 rows from LOG_ALARMAS
        cursor.execute("SELECT TOP 10 * FROM LOG_ALARMAS")
        rows = cursor.fetchall()
        print("First 10 rows in LOG_ALARMAS:")
        for row in rows:
            print(row)
            
        # 4. Get distinct values of TIPO
        cursor.execute("SELECT DISTINCT TIPO FROM LOG_ALARMAS")
        types = cursor.fetchall()
        print("Distinct values of TIPO:")
        for t in types:
            print(t)
            
except Exception as e:
    print("Error connecting/querying:", e)
