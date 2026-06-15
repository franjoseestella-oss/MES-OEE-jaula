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

query = """
SELECT 
    CAST(CAST('2026-06-08T13:00:00Z' AS datetimeoffset) AT TIME ZONE 'Romance Standard Time' AS DATETIME) AS [ToLocal],
    GETDATE() AS [LocalNow]
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    print(f"ToLocal (DATETIME): {row[0]}")
    print(f"LocalNow: {row[1]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
