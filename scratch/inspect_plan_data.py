import pyodbc
import json

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

print("=== JAULA_ERP ===")
cursor.execute("""
SELECT id, secuencia, bastidor, modelo, fecha_montaje 
FROM JAULA_ERP 
WHERE fecha_montaje BETWEEN '2026-06-15' AND '2026-06-19'
ORDER BY id
""")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, Secuencia: {r[1]}, Bastidor: {r[2]}, Modelo: {r[3]}, Fecha: {r[4]}")

print("\n=== LOG_TABLA ===")
cursor.execute("""
SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_MONTAJE, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC
FROM LOG_TABLA
WHERE FECHA_MONTAJE BETWEEN '2026-06-15' AND '2026-06-19'
ORDER BY id
""")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, Secuencia: {r[1]}, Bastidor: {r[2]}, OK_NOK: {r[3]}, Fecha: {r[4]}, Inicio: {r[5]}, Fin: {r[6]}")

print("\n=== CALENDARIO_LABORAL ===")
cursor.execute("""
SELECT Fecha, Tipo_Dia, Laborable, Cant_A_Fabricar
FROM CALENDARIO_LABORAL
WHERE Fecha BETWEEN '2026-06-15' AND '2026-06-19'
ORDER BY Fecha
""")
rows = cursor.fetchall()
for r in rows:
    print(f"Fecha: {r[0]}, Tipo_Dia: {r[1]}, Laborable: {r[2]}, Cant_A_Fabricar: {r[3]}")
