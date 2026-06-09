"""
Explorador de esquema — ejecútalo directamente en tu máquina Windows:

    pip install pyodbc
    python scripts/explore_db.py

Muestra las columnas de LOG_TABLA y las 5 últimas filas para que podamos
mapear los campos al modelo de OEE.
"""

import pyodbc
import sys

# Reconfigure stdout to support utf-8 output in Windows PowerShell/cmd
sys.stdout.reconfigure(encoding='utf-8')

SERVER   = r"DESKTOP-PMRMSPT\SQLEXPRESS"
DATABASE = "DAFEED"
TABLE    = "dbo.LOG_TABLA"

# ── Conexión con Windows Authentication (sin usuario/contraseña) ──────────────
# Si necesitas usuario SQL, cambia a:
# conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID=usuario;PWD=contraseña;TrustServerCertificate=yes"
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

print(f"\n{'='*60}")
print(f"  Conectando a  {SERVER}  /  {DATABASE}")
print(f"{'='*60}\n")

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    print("OK - Conexion OK\n")
except Exception as e:
    print(f"Error - Error de conexion: {e}")
    print("\nSi falla Windows Auth, edita conn_str con UID/PWD.")
    sys.exit(1)

# ── 1. Todas las tablas de DAFEED ─────────────────────────────────────────────
print("─── Tablas en DAFEED ───────────────────────────────────")
cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
""")
for row in cursor.fetchall():
    print(f"  {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

# ── 2. Columnas de LOG_TABLA ──────────────────────────────────────────────────
print(f"\n─── Columnas de {TABLE} ───────────────────────────────")
cursor.execute(f"""
    SELECT
        COLUMN_NAME,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'dbo'
      AND TABLE_NAME   = 'LOG_TABLA'
    ORDER BY ORDINAL_POSITION
""")
cols = cursor.fetchall()
print(f"  {'#':<4} {'Columna':<35} {'Tipo':<20} {'Nulo':<6} {'Default'}")
print(f"  {'-'*80}")
for i, c in enumerate(cols, 1):
    length = f"({c.CHARACTER_MAXIMUM_LENGTH})" if c.CHARACTER_MAXIMUM_LENGTH else ""
    print(f"  {i:<4} {c.COLUMN_NAME:<35} {c.DATA_TYPE+length:<20} {c.IS_NULLABLE:<6} {c.COLUMN_DEFAULT or ''}")

# ── 3. Últimas 5 filas ────────────────────────────────────────────────────────
print(f"\n─── Últimas 5 filas de {TABLE} ──────────────────────────")
try:
    cursor.execute(f"SELECT TOP 5 * FROM {TABLE} ORDER BY (SELECT NULL)")
    rows = cursor.fetchall()
    if rows:
        col_names = [desc[0] for desc in cursor.description]
        print("  " + " | ".join(f"{c[:20]:<20}" for c in col_names))
        print("  " + "-" * min(len(col_names) * 23, 120))
        for row in rows:
            print("  " + " | ".join(f"{str(v)[:20]:<20}" for v in row))
    else:
        print("  (tabla vacía)")
except Exception as e:
    print(f"  Error al leer filas: {e}")

# ── 4. Columnas de REFERENCIA_EN_CICLO (ciclo ideal) ─────────────────────────
print(f"\n─── Columnas de dbo.REFERENCIA_EN_CICLO ─────────────────")
try:
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'REFERENCIA_EN_CICLO'
        ORDER BY ORDINAL_POSITION
    """)
    for c in cursor.fetchall():
        print(f"  {c.COLUMN_NAME:<35} {c.DATA_TYPE}")
    cursor.execute("SELECT TOP 3 * FROM dbo.REFERENCIA_EN_CICLO")
    rows = cursor.fetchall()
    if rows:
        col_names = [desc[0] for desc in cursor.description]
        print("\n  " + " | ".join(f"{c[:20]:<20}" for c in col_names))
        for row in rows:
            print("  " + " | ".join(f"{str(v)[:20]:<20}" for v in row))
except Exception as e:
    print(f"  Error: {e}")

conn.close()
print(f"\n{'='*60}")
print("  Copia este output completo y compártelo para mapear los campos.")
print(f"{'='*60}\n")
