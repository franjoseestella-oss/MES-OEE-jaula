import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-PMRMSPT\\SQLEXPRESS;"
    "Database=DAFEED;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get column names and types for dbo.LOG_TABLA
cursor.execute("SELECT TOP 0 * FROM dbo.LOG_TABLA")
print("LOG_TABLA columns:", [col[0] for col in cursor.description])

# Fetch top 10 rows from LOG_TABLA
cursor.execute("SELECT TOP 10 * FROM dbo.LOG_TABLA ORDER BY id DESC")
print("LOG_TABLA recent rows:")
for r in cursor.fetchall():
    print(r)

# Check REFERENCIA_EN_CICLO columns and contents
cursor.execute("SELECT TOP 0 * FROM dbo.REFERENCIA_EN_CICLO")
print("REFERENCIA_EN_CICLO columns:", [col[0] for col in cursor.description])
cursor.execute("SELECT * FROM dbo.REFERENCIA_EN_CICLO")
print("REFERENCIA_EN_CICLO rows:")
for r in cursor.fetchall():
    print(r)

conn.close()
