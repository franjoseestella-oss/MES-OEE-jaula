import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT GETDATE() AS local_db, GETUTCDATE() AS utc_db, SYSDATETIME() AS sys_dt")
row = cursor.fetchone()
print("GETDATE():", row.local_db)
print("GETUTCDATE():", row.utc_db)
print("SYSDATETIME():", row.sys_dt)
cursor.close()
conn.close()
