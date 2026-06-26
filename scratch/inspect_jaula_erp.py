import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

query = """
SELECT id, secuencia, bastidor, modelo, fecha_montaje
FROM dbo.JAULA_ERP
WHERE TRY_CAST(secuencia AS INT) BETWEEN 225 AND 280
ORDER BY TRY_CAST(secuencia AS INT) ASC
"""

cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    print(r)

cursor.close()
conn.close()
