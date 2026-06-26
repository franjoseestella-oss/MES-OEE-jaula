import pyodbc
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get June 24 logs
cursor.execute("""
    SELECT id, NSECUENCIA, NBASTIDOR, FECHA_MONTAJE, OK_NOK 
    FROM dbo.LOG_TABLA 
    WHERE FECHA_MONTAJE = '2026-06-24'
    ORDER BY id
""")
logs = cursor.fetchall()
print("=== LOGS ON 2026-06-24 ===")
for l in logs:
    print(f"Log ID: {l[0]} | Seq: {l[1]} | Bastidor: {l[2]} | Fecha Montaje: {l[3]} | Status: {l[4]}")
    
    # Query ERP for this bastidor
    cursor.execute(f"SELECT id, secuencia, bastidor, modelo, fecha_montaje FROM dbo.JAULA_ERP WHERE bastidor = '{l[2]}'")
    erp_rows = cursor.fetchall()
    for erp in erp_rows:
        print(f"  -> ERP ID: {erp[0]} | Seq: {erp[1]} | Bastidor: {erp[2]} | Modelo: {erp[3]} | Fecha Montaje: {erp[4]}")

cursor.close()
conn.close()
