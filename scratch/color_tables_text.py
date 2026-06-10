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

# 1. Update SQL queries to put [Resultado] right after [ID]
sql_template_ok = (
    "SELECT id AS [ID], OK_NOK AS [Resultado], fecha_creacion AS [Fecha Creación], "
    "OPERARIO AS [Operario], NBASTIDOR AS [Bastidor], NMODELO AS [Modelo], NMASTIL AS [Mástil], "
    "PESO_PRUEBA AS [Peso (kg)], CARGA_GET AS [Carga Medida], "
    "TIEMPO_ELEVACION_MIN_SINCARGA AS [Elev Sin Carga Mín (s)], TIEMPO_ELEVACION_MEDIDO_SINCARGA AS [Elev Sin Carga (s)], TIEMPO_ELEVACION_MAX_SINCARGA AS [Elev Sin Carga Máx (s)], "
    "TIEMPO_DESCENSO_MIN_SINCARGA AS [Desc Sin Carga Mín (s)], TIEMPO_DESCENSO_MEDIDO_SINCARGA AS [Desc Sin Carga (s)], TIEMPO_DESCENSO_MAX_SINCARGA AS [Desc Sin Carga Máx (s)], "
    "TIEMPO_ELEVACION_MIN_CARGA AS [Elev Carga Mín (s)], TIEMPO_ELEVACION_MEDIDO_CARGA AS [Elev Carga (s)], TIEMPO_ELEVACION_MAX_CARGA AS [Elev Carga Máx (s)], "
    "TIEMPO_DESCENSO_MIN_CARGA AS [Desc Carga Mín (s)], TIEMPO_DESCENSO_MEDIDO_CARGA AS [Desc Carga (s)], TIEMPO_DESCENSO_MAX_CARGA AS [Desc Carga Máx (s)], "
    "DURACION_SEC AS [Duración] "
    "FROM LOG_TABLA WHERE fecha_creacion >= $__timeFrom() AND fecha_creacion <= $__timeTo() AND OK_NOK = 'OK' "
    "ORDER BY fecha_creacion DESC"
)

sql_template_nok = (
    "SELECT id AS [ID], OK_NOK AS [Resultado], fecha_creacion AS [Fecha Creación], "
    "OPERARIO AS [Operario], NBASTIDOR AS [Bastidor], NMODELO AS [Modelo], NMASTIL AS [Mástil], "
    "PESO_PRUEBA AS [Peso (kg)], CARGA_GET AS [Carga Medida], "
    "TIEMPO_ELEVACION_MIN_SINCARGA AS [Elev Sin Carga Mín (s)], TIEMPO_ELEVACION_MEDIDO_SINCARGA AS [Elev Sin Carga (s)], TIEMPO_ELEVACION_MAX_SINCARGA AS [Elev Sin Carga Máx (s)], "
    "TIEMPO_DESCENSO_MIN_SINCARGA AS [Desc Sin Carga Mín (s)], TIEMPO_DESCENSO_MEDIDO_SINCARGA AS [Desc Sin Carga (s)], TIEMPO_DESCENSO_MAX_SINCARGA AS [Desc Sin Carga Máx (s)], "
    "TIEMPO_ELEVACION_MIN_CARGA AS [Elev Carga Mín (s)], TIEMPO_ELEVACION_MEDIDO_CARGA AS [Elev Carga (s)], TIEMPO_ELEVACION_MAX_CARGA AS [Elev Carga Máx (s)], "
    "TIEMPO_DESCENSO_MIN_CARGA AS [Desc Carga Mín (s)], TIEMPO_DESCENSO_MEDIDO_CARGA AS [Desc Carga (s)], TIEMPO_DESCENSO_MAX_CARGA AS [Desc Carga Máx (s)], "
    "DURACION_SEC AS [Duración] "
    "FROM LOG_TABLA WHERE fecha_creacion >= $__timeFrom() AND fecha_creacion <= $__timeTo() AND OK_NOK = 'NOK' "
    "ORDER BY fecha_creacion DESC"
)

p9["targets"][0]["rawSql"] = sql_template_ok
p16["targets"][0]["rawSql"] = sql_template_nok

# 2. Update panel fieldConfigs to color text / cells
# For OK: green text default
p9["fieldConfig"]["defaults"]["color"] = {"mode": "fixed", "fixedColor": "#2FD06A"}
p9["fieldConfig"]["defaults"]["custom"]["cellOptions"] = {"type": "color-text"}

# For NOK: red text default
p16["fieldConfig"]["defaults"]["color"] = {"mode": "fixed", "fixedColor": "#E32636"}
p16["fieldConfig"]["defaults"]["custom"]["cellOptions"] = {"type": "color-text"}

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Updated queries and defaults for OK and NOK tables successfully!")
