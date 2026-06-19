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

cursor.execute("SELECT DISTINCT Cant_A_Fabricar FROM dbo.CALENDARIO_LABORAL WHERE Laborable = 1")
for r in cursor.fetchall():
    print(r)

print("\nDetail of calendar dates with Cant_A_Fabricar other than 18:")
cursor.execute("SELECT Fecha, Tipo_Dia, Laborable, Cant_A_Fabricar FROM dbo.CALENDARIO_LABORAL WHERE Laborable = 1 AND Cant_A_Fabricar <> 18")
for r in cursor.fetchall():
    print(r)

cursor.close()
conn.close()
