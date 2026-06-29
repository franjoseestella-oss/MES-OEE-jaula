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
    
    # Query LOG_ALARMAS
    cursor.execute("SELECT TOP 20 FECHA_Y_HORA, TIPO, DESCRIPCION, DURACION FROM dbo.LOG_ALARMAS ORDER BY id DESC;")
    rows = cursor.fetchall()
    print("--- LOG_ALARMAS (newest first by id) ---")
    for r in rows:
        print(f"FECHA_Y_HORA: {r[0]} | TIPO: {r[1]} | DESCRIPCION: {r[2]} | DURACION: {r[3]}")
        
    conn.close()
except Exception as e:
    print("Error:", e)
