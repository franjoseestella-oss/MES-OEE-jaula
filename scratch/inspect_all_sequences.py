import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC")
    rows = cursor.fetchall()
    print(f"Total rows in JAULA_ERP: {len(rows)}")
    for i, r in enumerate(rows):
        # Print first few, and rows around 227
        if i < 20 or (i > len(rows) - 20) or ('0227' in r[1]) or ('0292' in r[1]):
            print(f"Index {i}: {r}")
        
except Exception as e:
    print("Error:", e)
