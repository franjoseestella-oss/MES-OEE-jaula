import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = """
    UPDATE dbo.REFERENCIA_EN_CICLO
    SET 
        ETAPA_ACTUAL = 1,
        REFERENCIA_ACTUAL = '0',
        FECHA_INICIO_CICLO = '0',
        OPERARIO = '0',
        FECHA_MONTAJE = '0',
        NSECUENCIA = '0',
        NMODELO = '0',
        NBASTIDOR = '0',
        NMASTIL = '0',
        FECHA_HORA_INICIO_MULTILOAD = '0',
        FECHA_HORA_FIN_MULTILOAD = '0',
        ESTADO_MULTILOAD = '0',
        TIEMPO_ELEVACION_MIN_SINCARGA = 0.0,
        TIEMPO_ELEVACION_MAX_SINCARGA = 0.0,
        TIEMPO_ELEVACION_MEDIDO_SINCARGA = 0.0,
        AVG_ELEVACION_SINCARGA = 0.0,
        TIEMPO_DESCENSO_MIN_SINCARGA = 0.0,
        TIEMPO_DESCENSO_MAX_SINCARGA = 0.0,
        TIEMPO_DESCENSO_MEDIDO_SINCARGA = 0.0,
        AVG_DESCENSO_SINCARGA = 0.0,
        FECHA_HORA_INICIO_SINCARGA = '0',
        FECHA_HORA_FIN_SINCARGA = '0',
        ESTADO_SINCARGA = '0',
        TIEMPO_ELEVACION_MIN_CARGA = 0.0,
        TIEMPO_ELEVACION_MAX_CARGA = 0.0,
        TIEMPO_ELEVACION_MEDIDO_CARGA = 0.0,
        AVG_ELEVACION_CARGA = 0.0,
        TIEMPO_DESCENSO_MIN_CARGA = 0.0,
        TIEMPO_DESCENSO_MAX_CARGA = 0.0,
        TIEMPO_DESCENSO_MEDIDO_CARGA = 0.0,
        AVG_DESCENSO_CARGA = 0.0,
        FECHA_HORA_INICIO_CARGA = '0',
        FECHA_HORA_FIN_CARGA = '0',
        ESTADO_CARGA = '0',
        CARGA_CONSIGNADA = 0.0,
        CARGA_GET = 0.0,
        PESO_PRUEBA = 0.0,
        ALTURA_INICIAL = 0.0,
        ALTURA_FINAL = 0.0,
        DIFERENCIA_ALTURAS = 0.0,
        FECHA_HORA_INICIO_5MIN = '0',
        FECHA_HORA_FIN_5MIN = '0',
        ESTADO_CARGA_5_MIN = '0',
        REPETICIONES_SECUENCIA = 0,
        FECHA_HORA_INICIO_SEC = '0',
        FECHA_HORA_FIN_SEC = '0',
        DURACION_SEC = '0',
        OK_NOK = '0'
    WHERE id = 1;
    """
    cursor.execute(query)
    conn.commit()
    print("Successfully restored REFERENCIA_EN_CICLO to idle/reset state.")
except Exception as e:
    print("Error:", e)
