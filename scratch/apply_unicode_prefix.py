import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Find Panel 9 (OK) and Panel 16 (NOK)
p9 = None
p16 = None
for p in db.get("panels", []):
    if p.get("id") == 9:
        p9 = p
    elif p.get("id") == 16:
        p16 = p

if not p9 or not p16:
    raise ValueError("Panel 9 or Panel 16 not found in dashboard json")

# Define SQL queries with N'' prefix for Unicode strings in SQL Server
sql_select_template = (
    "SELECT id AS [ID], OK_NOK AS [Resultado], fecha_creacion AS [Fecha Creación], "
    "OPERARIO AS [Operario], NBASTIDOR AS [Bastidor], NMODELO AS [Modelo], NMASTIL AS [Mástil], "
    "PESO_PRUEBA AS [Peso (kg)], CARGA_GET AS [Carga Medida], "
    # Elev Sin Carga
    "TIEMPO_ELEVACION_MIN_SINCARGA AS [Elev Sin Carga Mín (s)], "
    "CASE "
    "  WHEN TIEMPO_ELEVACION_MEDIDO_SINCARGA IS NULL THEN '' "
    "  WHEN TIEMPO_ELEVACION_MIN_SINCARGA IS NULL OR TIEMPO_ELEVACION_MAX_SINCARGA IS NULL "
    "  THEN CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  WHEN TIEMPO_ELEVACION_MEDIDO_SINCARGA >= TIEMPO_ELEVACION_MIN_SINCARGA "
    "   AND TIEMPO_ELEVACION_MEDIDO_SINCARGA <= TIEMPO_ELEVACION_MAX_SINCARGA "
    "  THEN N'🟢 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  ELSE N'🔴 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "END AS [Elev Sin Carga (s)], "
    "TIEMPO_ELEVACION_MAX_SINCARGA AS [Elev Sin Carga Máx (s)], "
    # Desc Sin Carga
    "TIEMPO_DESCENSO_MIN_SINCARGA AS [Desc Sin Carga Mín (s)], "
    "CASE "
    "  WHEN TIEMPO_DESCENSO_MEDIDO_SINCARGA IS NULL THEN '' "
    "  WHEN TIEMPO_DESCENSO_MIN_SINCARGA IS NULL OR TIEMPO_DESCENSO_MAX_SINCARGA IS NULL "
    "  THEN CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  WHEN TIEMPO_DESCENSO_MEDIDO_SINCARGA >= TIEMPO_DESCENSO_MIN_SINCARGA "
    "   AND TIEMPO_DESCENSO_MEDIDO_SINCARGA <= TIEMPO_DESCENSO_MAX_SINCARGA "
    "  THEN N'🟢 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  ELSE N'🔴 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "END AS [Desc Sin Carga (s)], "
    "TIEMPO_DESCENSO_MAX_SINCARGA AS [Desc Sin Carga Máx (s)], "
    # Elev Carga
    "TIEMPO_ELEVACION_MIN_CARGA AS [Elev Carga Mín (s)], "
    "CASE "
    "  WHEN TIEMPO_ELEVACION_MEDIDO_CARGA IS NULL THEN '' "
    "  WHEN TIEMPO_ELEVACION_MIN_CARGA IS NULL OR TIEMPO_ELEVACION_MAX_CARGA IS NULL "
    "  THEN CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  WHEN TIEMPO_ELEVACION_MEDIDO_CARGA >= TIEMPO_ELEVACION_MIN_CARGA "
    "   AND TIEMPO_ELEVACION_MEDIDO_CARGA <= TIEMPO_ELEVACION_MAX_CARGA "
    "  THEN N'🟢 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  ELSE N'🔴 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "END AS [Elev Carga (s)], "
    "TIEMPO_ELEVACION_MAX_CARGA AS [Elev Carga Máx (s)], "
    # Desc Carga
    "TIEMPO_DESCENSO_MIN_CARGA AS [Desc Carga Mín (s)], "
    "CASE "
    "  WHEN TIEMPO_DESCENSO_MEDIDO_CARGA IS NULL THEN '' "
    "  WHEN TIEMPO_DESCENSO_MIN_CARGA IS NULL OR TIEMPO_DESCENSO_MAX_CARGA IS NULL "
    "  THEN CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  WHEN TIEMPO_DESCENSO_MEDIDO_CARGA >= TIEMPO_DESCENSO_MIN_CARGA "
    "   AND TIEMPO_DESCENSO_MEDIDO_CARGA <= TIEMPO_DESCENSO_MAX_CARGA "
    "  THEN N'🟢 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "  ELSE N'🔴 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s' "
    "END AS [Desc Carga (s)], "
    "TIEMPO_DESCENSO_MAX_CARGA AS [Desc Carga Máx (s)], "
    "DURACION_SEC AS [Duración] "
    "FROM LOG_TABLA WHERE fecha_creacion >= $__timeFrom() AND fecha_creacion <= $__timeTo() AND OK_NOK = '{status}' "
    "ORDER BY fecha_creacion DESC"
)

p9["targets"][0]["rawSql"] = sql_select_template.format(status="OK")
p16["targets"][0]["rawSql"] = sql_select_template.format(status="NOK")

# Write back to file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully updated queries with N prefix in log_dashboard.json!")
