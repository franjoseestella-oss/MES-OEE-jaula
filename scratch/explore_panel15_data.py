import pyodbc

SERVER   = r"DESKTOP-PMRMSPT\SQLEXPRESS"
DATABASE = "DAFEED"
TABLE    = "dbo.LOG_TABLA"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1
            TIEMPO_DESCENSO_MEDIDO_SINCARGA,
            TIEMPO_DESCENSO_MIN_SINCARGA,
            TIEMPO_DESCENSO_MAX_SINCARGA,
            fecha_creacion
        FROM LOG_TABLA
        ORDER BY fecha_creacion DESC
    """)
    row = cursor.fetchone()
    print("Row data:", row)
    print("Types:")
    for i, desc in enumerate(cursor.description):
        print(f"  {desc[0]}: {type(row[i])} (value: {row[i]})")
    conn.close()
except Exception as e:
    print("Error:", e)
