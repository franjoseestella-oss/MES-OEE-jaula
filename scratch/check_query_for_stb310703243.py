import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pyodbc
from test_updated_query import sql_query

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

cursor.execute(sql_query)
rows = cursor.fetchall()
found = False
for r in rows:
    if r[2] == 'STB310703243':
        print("Found in scheduler output:")
        print(r)
        found = True
if not found:
    print("STB310703243 NOT found in scheduler output!")

conn.close()
