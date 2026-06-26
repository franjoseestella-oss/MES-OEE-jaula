import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    print("--- JAULA_ERP recent rows ---")
    cursor.execute("SELECT TOP 10 id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP ORDER BY id DESC")
    for r in cursor.fetchall():
        print(r)

    print("\n--- LOG_TABLA recent rows ---")
    cursor.execute("SELECT TOP 10 id, NBASTIDOR, FECHA_MONTAJE, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC FROM dbo.LOG_TABLA ORDER BY id DESC")
    for r in cursor.fetchall():
        print(r)

    print("\n--- Selected bastidor data (SFB09E704641) ---")
    cursor.execute("SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor='SFB09E704641'")
    for r in cursor.fetchall():
        print(r)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
