import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
SELECT Fecha, Laborable, Cant_A_Fabricar
FROM CALENDARIO_LABORAL
WHERE Fecha BETWEEN '2026-06-15' AND '2026-06-19'
ORDER BY Fecha
""")
for r in cursor.fetchall():
    print(f"Fecha: {r[0]} Laborable: {r[1]} Cant: {r[2]}")
