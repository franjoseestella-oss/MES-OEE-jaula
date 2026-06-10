import pyodbc
from dotenv import dotenv_values

config = dotenv_values(".env")

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={config['SQL_SERVER_HOST']},{config['SQL_SERVER_PORT']};"
    f"DATABASE={config['SQL_SERVER_DATABASE']};"
    f"UID={config['SQL_SERVER_USER']};"
    f"PWD={config['SQL_SERVER_PASSWORD']};"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT '-Infinity' AS [Base]")
row = cursor.fetchone()
print("Row:", row)
print("Type:", type(row[0]))

conn.close()
