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
    
    # Query LOG_TABLA
    cursor.execute("SELECT TOP 20 id, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA ORDER BY id DESC;")
    rows = cursor.fetchall()
    print("--- LOG_TABLA (newest first by id) ---")
    for r in rows:
        print(f"ID: {r[0]} | NBASTIDOR: {r[1]} | FECHA_MONTAJE: {r[2]} | OK_NOK: {r[3]} | INICIO: {r[4]} | FIN: {r[5]}")
        
    conn.close()
except Exception as e:
    print("Error:", e)
