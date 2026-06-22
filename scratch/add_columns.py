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
    
    print("Adding columns to mes_machine_events...")
    
    # Check if columns already exist, add them if they don't
    columns_to_add = [
        ("secuencia_id", "VARCHAR(50)"),
        ("tiempo_teorico_s", "INT"),
        ("duracion_real_s", "INT"),
        ("dentro_de_tiempo", "BIT"),
        ("error", "VARCHAR(255)")
    ]
    
    for col_name, col_type in columns_to_add:
        # Check existence
        cursor.execute(f"""
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'mes_machine_events' AND COLUMN_NAME = '{col_name}'
        """)
        if not cursor.fetchone():
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE mes_machine_events ADD {col_name} {col_type} NULL;")
            conn.commit()
            print(f"Column {col_name} added successfully.")
        else:
            print(f"Column {col_name} already exists.")
            
    print("Done checking/adding columns.")
    conn.close()
except Exception as e:
    print(f"Error altering database: {e}")
