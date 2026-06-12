"""Script para crear e insertar el calendario laboral 2026 en la tabla CALENDARIO_LABORAL de DAFEED."""

import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

SERVER = os.getenv('SQL_SERVER_HOST', r'DESKTOP-PMRMSPT\SQLEXPRESS')
DATABASE = os.getenv('SQL_SERVER_DATABASE', 'DAFEED')
DRIVER = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
USER = os.getenv('SQL_SERVER_USER', '')
PASSWORD = os.getenv('SQL_SERVER_PASSWORD', '')
TRUST_CERT = os.getenv('SQL_SERVER_TRUST_CERT', 'yes')

# Datos del calendario laboral 2026
CALENDARIO_DATA = [
    ('2026-01-01','Festivo Abonable',0),
    ('2026-01-02','Festivo Pactado',0),
    ('2026-01-03','Fin de Semana',0),
    ('2026-01-04','Fin de Semana',0),
    ('2026-01-05','Laborable',1),
    ('2026-01-06','Festivo Abonable',0),
    ('2026-01-07','Laborable',1),
    ('2026-01-08','Laborable',1),
    ('2026-01-09','Laborable',1),
    ('2026-01-10','Fin de Semana',0),
    ('2026-01-11','Fin de Semana',0),
    ('2026-01-12','Laborable',1),
    ('2026-01-13','Laborable',1),
    ('2026-01-14','Laborable',1),
    ('2026-01-15','Laborable',1),
    ('2026-01-16','Laborable',1),
    ('2026-01-17','Fin de Semana',0),
    ('2026-01-18','Fin de Semana',0),
    ('2026-01-19','Laborable',1),
    ('2026-01-20','Laborable',1),
    ('2026-01-21','Laborable',1),
    ('2026-01-22','Laborable',1),
    ('2026-01-23','Laborable',1),
    ('2026-01-24','Fin de Semana',0),
    ('2026-01-25','Fin de Semana',0),
    ('2026-01-26','Laborable',1),
    ('2026-01-27','Laborable',1),
    ('2026-01-28','Laborable',1),
    ('2026-01-29','Laborable',1),
    ('2026-01-30','Laborable',1),
    ('2026-01-31','Fin de Semana',0),
    ('2026-02-01','Fin de Semana',0),
    ('2026-02-02','Laborable',1),
    ('2026-02-03','Laborable',1),
    ('2026-02-04','Laborable',1),
    ('2026-02-05','Laborable',1),
    ('2026-02-06','Laborable',1),
    ('2026-02-07','Fin de Semana',0),
    ('2026-02-08','Fin de Semana',0),
    ('2026-02-09','Laborable',1),
    ('2026-02-10','Laborable',1),
    ('2026-02-11','Laborable',1),
    ('2026-02-12','Laborable',1),
    ('2026-02-13','Laborable',1),
    ('2026-02-14','Fin de Semana',0),
    ('2026-02-15','Fin de Semana',0),
    ('2026-02-16','Laborable',1),
    ('2026-02-17','Laborable',1),
    ('2026-02-18','Laborable',1),
    ('2026-02-19','Laborable',1),
    ('2026-02-20','Laborable',1),
    ('2026-02-21','Fin de Semana',0),
    ('2026-02-22','Fin de Semana',0),
    ('2026-02-23','Laborable',1),
    ('2026-02-24','Laborable',1),
    ('2026-02-25','Laborable',1),
    ('2026-02-26','Laborable',1),
    ('2026-02-27','Laborable',1),
    ('2026-02-28','Fin de Semana',0),
    ('2026-03-01','Fin de Semana',0),
    ('2026-03-02','Laborable',1),
    ('2026-03-03','Laborable',1),
    ('2026-03-04','Laborable',1),
    ('2026-03-05','Laborable',1),
    ('2026-03-06','Laborable',1),
    ('2026-03-07','Fin de Semana',0),
    ('2026-03-08','Fin de Semana',0),
    ('2026-03-09','Laborable',1),
    ('2026-03-10','Laborable',1),
    ('2026-03-11','Laborable',1),
    ('2026-03-12','Laborable',1),
    ('2026-03-13','Laborable',1),
    ('2026-03-14','Fin de Semana',0),
    ('2026-03-15','Fin de Semana',0),
    ('2026-03-16','Laborable',1),
    ('2026-03-17','Laborable',1),
    ('2026-03-18','Laborable',1),
    ('2026-03-19','Festivo Abonable',0),
    ('2026-03-20','Festivo Pactado',0),
    ('2026-03-21','Fin de Semana',0),
    ('2026-03-22','Fin de Semana',0),
    ('2026-03-23','Laborable',1),
    ('2026-03-24','Laborable',1),
    ('2026-03-25','Laborable',1),
    ('2026-03-26','Laborable',1),
    ('2026-03-27','Laborable',1),
    ('2026-03-28','Fin de Semana',0),
    ('2026-03-29','Fin de Semana',0),
    ('2026-03-30','Laborable',1),
    ('2026-03-31','Laborable',1),
    ('2026-04-01','Laborable',1),
    ('2026-04-02','Festivo Abonable',0),
    ('2026-04-03','Festivo Abonable',0),
    ('2026-04-04','Fin de Semana',0),
    ('2026-04-05','Fin de Semana',0),
    ('2026-04-06','Festivo Abonable',0),
    ('2026-04-07','Laborable',1),
    ('2026-04-08','Laborable',1),
    ('2026-04-09','Laborable',1),
    ('2026-04-10','Laborable',1),
    ('2026-04-11','Fin de Semana',0),
    ('2026-04-12','Fin de Semana',0),
    ('2026-04-13','Laborable',1),
    ('2026-04-14','Laborable',1),
    ('2026-04-15','Laborable',1),
    ('2026-04-16','Laborable',1),
    ('2026-04-17','Laborable',1),
    ('2026-04-18','Fin de Semana',0),
    ('2026-04-19','Fin de Semana',0),
    ('2026-04-20','Laborable',1),
    ('2026-04-21','Laborable',1),
    ('2026-04-22','Laborable',1),
    ('2026-04-23','Laborable',1),
    ('2026-04-24','Laborable',1),
    ('2026-04-25','Fin de Semana',0),
    ('2026-04-26','Fin de Semana',0),
    ('2026-04-27','Laborable',1),
    ('2026-04-28','Laborable',1),
    ('2026-04-29','Laborable',1),
    ('2026-04-30','Laborable',1),
    ('2026-05-01','Festivo Abonable',0),
    ('2026-05-02','Fin de Semana',0),
    ('2026-05-03','Fin de Semana',0),
    ('2026-05-04','Laborable',1),
    ('2026-05-05','Laborable',1),
    ('2026-05-06','Laborable',1),
    ('2026-05-07','Laborable',1),
    ('2026-05-08','Laborable',1),
    ('2026-05-09','Fin de Semana',0),
    ('2026-05-10','Fin de Semana',0),
    ('2026-05-11','Laborable',1),
    ('2026-05-12','Laborable',1),
    ('2026-05-13','Laborable',1),
    ('2026-05-14','Laborable',1),
    ('2026-05-15','Laborable',1),
    ('2026-05-16','Fin de Semana',0),
    ('2026-05-17','Fin de Semana',0),
    ('2026-05-18','Laborable',1),
    ('2026-05-19','Laborable',1),
    ('2026-05-20','Laborable',1),
    ('2026-05-21','Laborable',1),
    ('2026-05-22','Laborable',1),
    ('2026-05-23','Fin de Semana',0),
    ('2026-05-24','Fin de Semana',0),
    ('2026-05-25','Laborable',1),
    ('2026-05-26','Laborable',1),
    ('2026-05-27','Laborable',1),
    ('2026-05-28','Laborable',1),
    ('2026-05-29','Laborable',1),
    ('2026-05-30','Fin de Semana',0),
    ('2026-05-31','Fin de Semana',0),
    ('2026-06-01','Laborable',1),
    ('2026-06-02','Laborable',1),
    ('2026-06-03','Laborable',1),
    ('2026-06-04','Laborable',1),
    ('2026-06-05','Laborable',1),
    ('2026-06-06','Fin de Semana',0),
    ('2026-06-07','Fin de Semana',0),
    ('2026-06-08','Laborable',1),
    ('2026-06-09','Laborable',1),
    ('2026-06-10','Laborable',1),
    ('2026-06-11','Laborable',1),
    ('2026-06-12','Laborable',1),
    ('2026-06-13','Fin de Semana',0),
    ('2026-06-14','Fin de Semana',0),
    ('2026-06-15','Laborable',1),
    ('2026-06-16','Laborable',1),
    ('2026-06-17','Laborable',1),
    ('2026-06-18','Laborable',1),
    ('2026-06-19','Laborable',1),
    ('2026-06-20','Fin de Semana',0),
    ('2026-06-21','Fin de Semana',0),
    ('2026-06-22','Laborable',1),
    ('2026-06-23','Laborable',1),
    ('2026-06-24','Laborable',1),
    ('2026-06-25','Laborable',1),
    ('2026-06-26','Laborable',1),
    ('2026-06-27','Fin de Semana',0),
    ('2026-06-28','Fin de Semana',0),
    ('2026-06-29','Laborable',1),
    ('2026-06-30','Laborable',1),
    ('2026-07-01','Laborable',1),
    ('2026-07-02','Laborable',1),
    ('2026-07-03','Laborable',1),
    ('2026-07-04','Fin de Semana',0),
    ('2026-07-05','Fin de Semana',0),
    ('2026-07-06','Vacaciones',0),
    ('2026-07-07','Vacaciones',0),
    ('2026-07-08','Vacaciones',0),
    ('2026-07-09','Vacaciones',0),
    ('2026-07-10','Vacaciones',0),
    ('2026-07-11','Fin de Semana',0),
    ('2026-07-12','Fin de Semana',0),
    ('2026-07-13','Laborable',1),
    ('2026-07-14','Laborable',1),
    ('2026-07-15','Laborable',1),
    ('2026-07-16','Laborable',1),
    ('2026-07-17','Laborable',1),
    ('2026-07-18','Fin de Semana',0),
    ('2026-07-19','Fin de Semana',0),
    ('2026-07-20','Laborable',1),
    ('2026-07-21','Laborable',1),
    ('2026-07-22','Laborable',1),
    ('2026-07-23','Laborable',1),
    ('2026-07-24','Laborable',1),
    ('2026-07-25','Fin de Semana',0),
    ('2026-07-26','Fin de Semana',0),
    ('2026-07-27','Laborable',1),
    ('2026-07-28','Laborable',1),
    ('2026-07-29','Laborable',1),
    ('2026-07-30','Laborable',1),
    ('2026-07-31','Laborable',1),
    ('2026-08-01','Vacaciones',0),
    ('2026-08-02','Fin de Semana',0),
    ('2026-08-03','Vacaciones',0),
    ('2026-08-04','Vacaciones',0),
    ('2026-08-05','Vacaciones',0),
    ('2026-08-06','Vacaciones',0),
    ('2026-08-07','Vacaciones',0),
    ('2026-08-08','Vacaciones',0),
    ('2026-08-09','Fin de Semana',0),
    ('2026-08-10','Vacaciones',0),
    ('2026-08-11','Vacaciones',0),
    ('2026-08-12','Vacaciones',0),
    ('2026-08-13','Vacaciones',0),
    ('2026-08-14','Vacaciones',0),
    ('2026-08-15','Festivo Abonable',0),
    ('2026-08-16','Fin de Semana',0),
    ('2026-08-17','Vacaciones',0),
    ('2026-08-18','Vacaciones',0),
    ('2026-08-19','Vacaciones',0),
    ('2026-08-20','Vacaciones',0),
    ('2026-08-21','Vacaciones',0),
    ('2026-08-22','Vacaciones',0),
    ('2026-08-23','Fin de Semana',0),
    ('2026-08-24','Vacaciones',0),
    ('2026-08-25','Vacaciones',0),
    ('2026-08-26','Vacaciones',0),
    ('2026-08-27','Vacaciones',0),
    ('2026-08-28','Vacaciones',0),
    ('2026-08-29','Fin de Semana',0),
    ('2026-08-30','Fin de Semana',0),
    ('2026-08-31','Vacaciones',0),
    ('2026-09-01','Laborable',1),
    ('2026-09-02','Laborable',1),
    ('2026-09-03','Laborable',1),
    ('2026-09-04','Laborable',1),
    ('2026-09-05','Fin de Semana',0),
    ('2026-09-06','Fin de Semana',0),
    ('2026-09-07','Laborable',1),
    ('2026-09-08','Laborable',1),
    ('2026-09-09','Laborable',1),
    ('2026-09-10','Laborable',1),
    ('2026-09-11','Laborable',1),
    ('2026-09-12','Fin de Semana',0),
    ('2026-09-13','Fin de Semana',0),
    ('2026-09-14','Laborable',1),
    ('2026-09-15','Laborable',1),
    ('2026-09-16','Laborable',1),
    ('2026-09-17','Laborable',1),
    ('2026-09-18','Laborable',1),
    ('2026-09-19','Fin de Semana',0),
    ('2026-09-20','Fin de Semana',0),
    ('2026-09-21','Laborable',1),
    ('2026-09-22','Laborable',1),
    ('2026-09-23','Laborable',1),
    ('2026-09-24','Laborable',1),
    ('2026-09-25','Laborable',1),
    ('2026-09-26','Fin de Semana',0),
    ('2026-09-27','Fin de Semana',0),
    ('2026-09-28','Laborable',1),
    ('2026-09-29','Laborable',1),
    ('2026-09-30','Laborable',1),
    ('2026-10-01','Laborable',1),
    ('2026-10-02','Laborable',1),
    ('2026-10-03','Fin de Semana',0),
    ('2026-10-04','Fin de Semana',0),
    ('2026-10-05','Laborable',1),
    ('2026-10-06','Laborable',1),
    ('2026-10-07','Laborable',1),
    ('2026-10-08','Laborable',1),
    ('2026-10-09','Laborable',1),
    ('2026-10-10','Fin de Semana',0),
    ('2026-10-11','Fin de Semana',0),
    ('2026-10-12','Festivo Abonable',0),
    ('2026-10-13','Laborable',1),
    ('2026-10-14','Laborable',1),
    ('2026-10-15','Laborable',1),
    ('2026-10-16','Laborable',1),
    ('2026-10-17','Fin de Semana',0),
    ('2026-10-18','Fin de Semana',0),
    ('2026-10-19','Laborable',1),
    ('2026-10-20','Laborable',1),
    ('2026-10-21','Laborable',1),
    ('2026-10-22','Laborable',1),
    ('2026-10-23','Laborable',1),
    ('2026-10-24','Fin de Semana',0),
    ('2026-10-25','Fin de Semana',0),
    ('2026-10-26','Laborable',1),
    ('2026-10-27','Laborable',1),
    ('2026-10-28','Laborable',1),
    ('2026-10-29','Laborable',1),
    ('2026-10-30','Laborable',1),
    ('2026-10-31','Fin de Semana',0),
    ('2026-11-01','Fin de Semana',0),
    ('2026-11-02','Festivo Abonable',0),
    ('2026-11-03','Laborable',1),
    ('2026-11-04','Laborable',1),
    ('2026-11-05','Laborable',1),
    ('2026-11-06','Laborable',1),
    ('2026-11-07','Fin de Semana',0),
    ('2026-11-08','Fin de Semana',0),
    ('2026-11-09','Laborable',1),
    ('2026-11-10','Laborable',1),
    ('2026-11-11','Laborable',1),
    ('2026-11-12','Laborable',1),
    ('2026-11-13','Laborable',1),
    ('2026-11-14','Fin de Semana',0),
    ('2026-11-15','Fin de Semana',0),
    ('2026-11-16','Laborable',1),
    ('2026-11-17','Laborable',1),
    ('2026-11-18','Laborable',1),
    ('2026-11-19','Laborable',1),
    ('2026-11-20','Laborable',1),
    ('2026-11-21','Fin de Semana',0),
    ('2026-11-22','Fin de Semana',0),
    ('2026-11-23','Laborable',1),
    ('2026-11-24','Laborable',1),
    ('2026-11-25','Laborable',1),
    ('2026-11-26','Laborable',1),
    ('2026-11-27','Laborable',1),
    ('2026-11-28','Fin de Semana',0),
    ('2026-11-29','Fin de Semana',0),
    ('2026-11-30','Laborable',1),
    ('2026-12-01','Laborable',1),
    ('2026-12-02','Laborable',1),
    ('2026-12-03','Festivo Abonable',0),
    ('2026-12-04','Festivo Pactado',0),
    ('2026-12-05','Fin de Semana',0),
    ('2026-12-06','Fin de Semana',0),
    ('2026-12-07','Festivo Pactado',0),
    ('2026-12-08','Festivo Abonable',0),
    ('2026-12-09','Laborable',1),
    ('2026-12-10','Laborable',1),
    ('2026-12-11','Laborable',1),
    ('2026-12-12','Fin de Semana',0),
    ('2026-12-13','Fin de Semana',0),
    ('2026-12-14','Laborable',1),
    ('2026-12-15','Laborable',1),
    ('2026-12-16','Laborable',1),
    ('2026-12-17','Laborable',1),
    ('2026-12-18','Laborable',1),
    ('2026-12-19','Fin de Semana',0),
    ('2026-12-20','Fin de Semana',0),
    ('2026-12-21','Laborable',1),
    ('2026-12-22','Laborable',1),
    ('2026-12-23','Laborable',1),
    ('2026-12-24','Festivo Pactado',0),
    ('2026-12-25','Festivo Abonable',0),
    ('2026-12-26','Fin de Semana',0),
    ('2026-12-27','Fin de Semana',0),
    ('2026-12-28','Festivo Pactado',0),
    ('2026-12-29','Festivo Pactado',0),
    ('2026-12-30','Festivo Pactado',0),
    ('2026-12-31','Festivo Pactado',0),
]


def main():
    # Construir cadena de conexión
    if USER and PASSWORD:
        conn_str = (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            f"TrustServerCertificate={TRUST_CERT};"
        )
    else:
        conn_str = (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate={TRUST_CERT};"
        )

    print(f"Conectando a {SERVER} / {DATABASE} ...")
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # 1. Crear tabla si no existe
    create_sql = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CALENDARIO_LABORAL')
    BEGIN
        CREATE TABLE dbo.CALENDARIO_LABORAL (
            Fecha       DATE         NOT NULL PRIMARY KEY,
            Tipo_Dia    VARCHAR(50)  NOT NULL,
            Laborable   BIT          NOT NULL DEFAULT 0
        );
        PRINT 'Tabla CALENDARIO_LABORAL creada.';
    END
    ELSE
    BEGIN
        PRINT 'Tabla CALENDARIO_LABORAL ya existe.';
    END
    """
    cursor.execute(create_sql)
    conn.commit()
    print("[OK] Tabla CALENDARIO_LABORAL verificada/creada.")

    # 2. Limpiar datos anteriores e insertar nuevos
    cursor.execute("DELETE FROM dbo.CALENDARIO_LABORAL")
    conn.commit()
    print("[OK] Datos anteriores eliminados.")

    # 3. Insertar todos los registros
    insert_sql = "INSERT INTO dbo.CALENDARIO_LABORAL (Fecha, Tipo_Dia, Laborable) VALUES (?, ?, ?)"
    cursor.executemany(insert_sql, CALENDARIO_DATA)
    conn.commit()
    print(f"[OK] {len(CALENDARIO_DATA)} registros insertados correctamente.")

    # 4. Verificar
    cursor.execute("SELECT COUNT(*) FROM dbo.CALENDARIO_LABORAL")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dbo.CALENDARIO_LABORAL WHERE Laborable = 1")
    laborables = cursor.fetchone()[0]
    cursor.execute("SELECT Tipo_Dia, COUNT(*) AS cnt FROM dbo.CALENDARIO_LABORAL GROUP BY Tipo_Dia ORDER BY cnt DESC")
    tipos = cursor.fetchall()

    print(f"\nResumen:")
    print(f"   Total días: {total}")
    print(f"   Días laborables: {laborables}")
    print(f"   Días no laborables: {total - laborables}")
    print(f"\n   Desglose por tipo:")
    for tipo, cnt in tipos:
        print(f"     {tipo}: {cnt}")

    cursor.close()
    conn.close()
    print("\n[OK] Calendario laboral 2026 insertado con exito en DAFEED.dbo.CALENDARIO_LABORAL!")


if __name__ == "__main__":
    main()
