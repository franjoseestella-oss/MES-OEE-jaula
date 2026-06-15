import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)

def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    families = {
        "M11": "(NMODELO LIKE 'FD%' OR NMODELO LIKE 'FG%')",
        "XL": "(NMODELO LIKE 'XL%')",
        "M2": "(NMODELO LIKE 'MX%')"
    }
    
    for name, cond in families.items():
        cursor.execute(f"SELECT COUNT(*) FROM LOG_TABLA WHERE OK_NOK = 'OK' AND {cond}")
        print(f"Family {name} OK count: {cursor.fetchone()[0]}")
        
    conn.close()

if __name__ == '__main__':
    main()
