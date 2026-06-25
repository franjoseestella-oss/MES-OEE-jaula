import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

def inspect():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("=== CALENDARIO_LABORAL FROM 2026-06-24 ===")
    cursor.execute("""
        SELECT Fecha, Tipo_Dia, Laborable, Cant_A_Fabricar
        FROM CALENDARIO_LABORAL
        WHERE Fecha >= '2026-06-24'
        ORDER BY Fecha ASC
    """)
    for r in cursor.fetchall():
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
