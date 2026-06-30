import pyodbc
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-PMRMSPT\\SQLEXPRESS;Database=DAFEED;Trusted_Connection=yes;TrustServerCertificate=yes')
c = conn.cursor()
c.execute("SELECT id, NBASTIDOR, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, OK_NOK FROM LOG_TABLA WHERE FECHA_HORA_INICIO_SEC LIKE '2026-06-26%'")
print("LOG_TABLA rows for 2026-06-26:")
for r in c.fetchall():
    print(r)
conn.close()
