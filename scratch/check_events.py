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
    
    print("Checking events in mes_machine_events for sequence '0245':")
    cursor.execute("SELECT id, timestamp, secuencia_id, state FROM dbo.mes_machine_events WHERE secuencia_id = '0245' ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    for r in rows:
        print(r)
        
    print("\nChecking the latest 10 events in mes_machine_events overall:")
    cursor.execute("SELECT TOP 10 id, timestamp, secuencia_id, state FROM dbo.mes_machine_events ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    for r in rows:
        print(r)
        
    conn.close()

if __name__ == "__main__":
    inspect()
