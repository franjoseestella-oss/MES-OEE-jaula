import pyodbc
import dotenv
import os
import re

dotenv.load_dotenv()

host = os.getenv("SQL_SERVER_HOST", "DESKTOP-PMRMSPT\\SQLEXPRESS")
database = os.getenv("SQL_SERVER_DATABASE", "DAFEED")
user = os.getenv("SQL_SERVER_USER", "usuario_readonly")
password = os.getenv("SQL_SERVER_PASSWORD", "Logisnext2026!")
driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")

# Let's connect using localhost if it's running locally, or the host
# Wait, is the host local? Yes, DESKTOP-PMRMSPT\SQLEXPRESS is local to the windows machine
conn_str = f"DRIVER={{{driver}}};SERVER={host};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"
print("Connecting with connection string:", conn_str.replace(password, "XXXXX"))

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connection successful!")
    
    # Read query_to_run.sql
    with open("scratch/query_to_run.sql", "r", encoding="utf-8") as f:
        query = f.read()
        
    print("Executing query...")
    cursor.execute(query)
    
    rows = None
    while True:
        try:
            rows = cursor.fetchall()
            break
        except pyodbc.Error as e:
            if not cursor.nextset():
                break
                
    if rows is not None:
        print(f"Query returned {len(rows)} rows.")
        for i, row in enumerate(rows[:20]):
            print(f"Row {i}: {row}")
    else:
        print("No result sets found.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print("Error executing query:", e)
