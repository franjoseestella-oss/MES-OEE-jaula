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
    
    print("=== Last 5 rows from JAULA_ERP ===")
    cursor.execute("SELECT TOP 5 * FROM dbo.JAULA_ERP ORDER BY id DESC")
    columns = [desc[0] for desc in cursor.description]
    print(columns)
    for row in cursor.fetchall():
        print(row)
        
    print("\n=== Last 5 rows from LOG_TABLA ===")
    cursor.execute("SELECT TOP 5 * FROM dbo.LOG_TABLA ORDER BY id DESC")
    columns = [desc[0] for desc in cursor.description]
    print(columns)
    for row in cursor.fetchall():
        print(row)
        
    print("\n=== Active Reference ===")
    cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
    columns = [desc[0] for desc in cursor.description]
    print(columns)
    for row in cursor.fetchall():
        print(row)

    print("\n=== WORK TURN ===")
    cursor.execute("SELECT * FROM dbo.TURNO_TRABAJO")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()
except Exception as e:
    print("Error:", e)
