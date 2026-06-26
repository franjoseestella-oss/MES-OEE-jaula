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

# Get LOG_TABLA column types
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'LOG_TABLA'")
print("LOG_TABLA columns:")
for r in cursor.fetchall():
    print(r)

# Get JAULA_ERP column types
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'JAULA_ERP'")
print("\nJAULA_ERP columns:")
for r in cursor.fetchall():
    print(r)

cursor.close()
conn.close()
