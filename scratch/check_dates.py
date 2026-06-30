import pyodbc
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-PMRMSPT\\SQLEXPRESS;Database=DAFEED;Trusted_Connection=yes;TrustServerCertificate=yes')
c = conn.cursor()
c.execute("SELECT TOP 20 SUBSTRING(FECHA_HORA_INICIO_SEC, 1, 10), COUNT(*) FROM LOG_TABLA GROUP BY SUBSTRING(FECHA_HORA_INICIO_SEC, 1, 10) ORDER BY SUBSTRING(FECHA_HORA_INICIO_SEC, 1, 10) DESC")
print("LOG_TABLA dates:")
for r in c.fetchall():
    print(r)
conn.close()
