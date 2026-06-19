import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def inspect_table(table_name):
    print(f"\n=================== TABLE: {table_name} ===================")
    cursor.execute(f"SELECT TOP 0 * FROM {table_name}")
    columns = [col[0] for col in cursor.description]
    print(f"Columns: {columns}")
    
    cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

inspect_table("dbo.JAULA_ERP")
inspect_table("dbo.HHSS_18")
inspect_table("dbo.HHSS_18_5")
inspect_table("dbo.HHSS_19")
inspect_table("dbo.TURNO_TRABAJO")

cursor.close()
conn.close()
