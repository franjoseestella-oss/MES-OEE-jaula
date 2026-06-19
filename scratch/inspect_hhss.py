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

def dump_table(table_name):
    print(f"\n=================== {table_name} ===================")
    cursor.execute(f"SELECT n_maq, horario FROM {table_name} ORDER BY n_maq")
    for r in cursor.fetchall():
        print(f"Seq: {r[0]} | Time: {r[1]}")

dump_table("dbo.HHSS_18")
dump_table("dbo.HHSS_18_5")
dump_table("dbo.HHSS_19")

cursor.close()
conn.close()
