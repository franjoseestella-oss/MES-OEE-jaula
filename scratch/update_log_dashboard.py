import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Locate Panel 14
panel_14 = None
for p in db.get("panels", []):
    if p.get("id") == 14:
        panel_14 = p
        break

if not panel_14:
    raise ValueError("Panel 14 not found in dashboard json")

# 1. Update options
panel_14["options"]["displayMode"] = "gradient"
panel_14["options"]["showThresholdLabels"] = True
panel_14["options"]["showThresholdMarkers"] = True

# 2. Update target SQL query to remove accents
unaccented_sql = (
    "SELECT TOP 1 "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [Elevacion Sin Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [Elevacion Sin Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [Descenso Sin Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [Descenso Sin Carga Max], "
    "COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga], "
    "COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [Elevacion Con Carga Min], "
    "COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [Elevacion Con Carga Max], "
    "COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga], "
    "COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [Descenso Con Carga Min], "
    "COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [Descenso Con Carga Max] "
    "FROM LOG_TABLA "
    "WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') "
    "ORDER BY fecha_creacion DESC"
)

for target in panel_14.get("targets", []):
    target["rawSql"] = unaccented_sql

# 3. Update transformations: replace "Elevación" with "Elevacion" in field names and mappings
for trans in panel_14.get("transformations", []):
    if trans.get("id") == "configFromData":
        opts = trans.get("options", {})
        apply_to = opts.get("applyTo", {})
        if apply_to.get("id") == "byName" and "Elevación" in apply_to.get("options", ""):
            apply_to["options"] = apply_to["options"].replace("Elevación", "Elevacion")
        
        for mapping in opts.get("mappings", []):
            field_name = mapping.get("fieldName", "")
            if "Elevación" in field_name:
                mapping["fieldName"] = field_name.replace("Elevación", "Elevacion")
                
    elif trans.get("id") == "filterFieldsByName":
        opts = trans.get("options", {})
        include = opts.get("include", {})
        names = include.get("names", [])
        for i, name in enumerate(names):
            if "Elevación" in name:
                names[i] = name.replace("Elevación", "Elevacion")

# Write back to log_dashboard.json
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully updated log_dashboard.json Panel 14!")
