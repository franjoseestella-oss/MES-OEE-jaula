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
    
    # Query current progress time/active sequence
    cursor.execute("SELECT TOP 5 * FROM dbo.HISTORICO_PROCESO ORDER BY id DESC;")
    rows = cursor.fetchall()
    print("--- HISTORICO_PROCESO (newest first) ---")
    for r in rows:
        print(r)
        
    conn.close()
except Exception as e:
    print("Error:", e)
