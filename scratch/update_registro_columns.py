import json
import os
import sys

# Ensure UTF-8 stdout encoding if possible
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

dashboard_path = "grafana/provisioning/dashboards/registro_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Define the common SELECT fields
select_fields = """SELECT
  id AS id,
  OPERARIO AS OPERARIO,
  COALESCE(CONVERT(varchar(10), TRY_CAST(FECHA_MONTAJE AS DATE), 103), '') AS FECHA_MONTAJE,
  NSECUENCIA AS NSECUENCIA,
  NMODELO AS NMODELO,
  NBASTIDOR AS NBASTIDOR,
  NMASTIL AS NMASTIL,
  ALTURA_MAX_INTERMEDIA AS ALTURA_MAX_INTERMEDIA,
  ESTADO_MULTILOAD AS ESTADO_MULTILOAD,
  TIEMPO_ELEVACION_MIN_SINCARGA AS TIEMPO_ELEVACION_MIN_SINCARGA,
  TIEMPO_ELEVACION_MAX_SINCARGA AS TIEMPO_ELEVACION_MAX_SINCARGA,
  CASE
    WHEN TIEMPO_ELEVACION_MEDIDO_SINCARGA IS NULL THEN ''
    WHEN TIEMPO_ELEVACION_MIN_SINCARGA IS NULL OR TIEMPO_ELEVACION_MAX_SINCARGA IS NULL
    THEN CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    WHEN TIEMPO_ELEVACION_MEDIDO_SINCARGA >= TIEMPO_ELEVACION_MIN_SINCARGA
     AND TIEMPO_ELEVACION_MEDIDO_SINCARGA <= TIEMPO_ELEVACION_MAX_SINCARGA
    THEN N'🟢 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    ELSE N'🔴 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
  END AS TIEMPO_ELEVACION_MEDIDO_SINCARGA,
  TIEMPO_DESCENSO_MIN_SINCARGA AS TIEMPO_DESCENSO_MIN_SINCARGA,
  TIEMPO_DESCENSO_MAX_SINCARGA AS TIEMPO_DESCENSO_MAX_SINCARGA,
  CASE
    WHEN TIEMPO_DESCENSO_MEDIDO_SINCARGA IS NULL THEN ''
    WHEN TIEMPO_DESCENSO_MIN_SINCARGA IS NULL OR TIEMPO_DESCENSO_MAX_SINCARGA IS NULL
    THEN CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    WHEN TIEMPO_DESCENSO_MEDIDO_SINCARGA >= TIEMPO_DESCENSO_MIN_SINCARGA
     AND TIEMPO_DESCENSO_MEDIDO_SINCARGA <= TIEMPO_DESCENSO_MAX_SINCARGA
    THEN N'🟢 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    ELSE N'🔴 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_SINCARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
  END AS TIEMPO_DESCENSO_MEDIDO_SINCARGA,
  ESTADO_SINCARGA AS ESTADO_SINCARGA,
  TIEMPO_ELEVACION_MIN_CARGA AS TIEMPO_ELEVACION_MIN_CARGA,
  TIEMPO_ELEVACION_MAX_CARGA AS TIEMPO_ELEVACION_MAX_CARGA,
  CASE
    WHEN TIEMPO_ELEVACION_MEDIDO_CARGA IS NULL THEN ''
    WHEN TIEMPO_ELEVACION_MIN_CARGA IS NULL OR TIEMPO_ELEVACION_MAX_CARGA IS NULL
    THEN CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    WHEN TIEMPO_ELEVACION_MEDIDO_CARGA >= TIEMPO_ELEVACION_MIN_CARGA
     AND TIEMPO_ELEVACION_MEDIDO_CARGA <= TIEMPO_ELEVACION_MAX_CARGA
    THEN N'🟢 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    ELSE N'🔴 ' + CAST(CAST(TIEMPO_ELEVACION_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
  END AS TIEMPO_ELEVACION_MEDIDO_CARGA,
  TIEMPO_DESCENSO_MIN_CARGA AS TIEMPO_DESCENSO_MIN_CARGA,
  TIEMPO_DESCENSO_MAX_CARGA AS TIEMPO_DESCENSO_MAX_CARGA,
  CASE
    WHEN TIEMPO_DESCENSO_MEDIDO_CARGA IS NULL THEN ''
    WHEN TIEMPO_DESCENSO_MIN_CARGA IS NULL OR TIEMPO_DESCENSO_MAX_CARGA IS NULL
    THEN CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    WHEN TIEMPO_DESCENSO_MEDIDO_CARGA >= TIEMPO_DESCENSO_MIN_CARGA
     AND TIEMPO_DESCENSO_MEDIDO_CARGA <= TIEMPO_DESCENSO_MAX_CARGA
    THEN N'🟢 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
    ELSE N'🔴 ' + CAST(CAST(TIEMPO_DESCENSO_MEDIDO_CARGA AS DECIMAL(10,2)) AS VARCHAR) + ' s'
  END AS TIEMPO_DESCENSO_MEDIDO_CARGA,
  ESTADO_CARGA AS ESTADO_CARGA,
  CARGA_CONSIGNADA AS CARGA_CONSIGNADA,
  CARGA_GET AS CARGA_GET,
  PESO_PRUEBA AS PESO_PRUEBA,
  ALTURA_INICIAL AS ALTURA_INICIAL,
  ALTURA_FINAL AS ALTURA_FINAL,
  DIFERENCIA_ALTURAS AS DIFERENCIA_ALTURAS,
  ESTADO_CARGA_5_MIN AS ESTADO_CARGA_5_MIN,
  FECHA_HORA_INICIO_SEC AS FECHA_HORA_INICIO_SEC,
  FECHA_HORA_FIN_SEC AS FECHA_HORA_FIN_SEC,
  DURACION_SEC AS DURACION_SEC,
  OK_NOK AS OK_NOK
FROM LOG_TABLA"""

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

# Process each panel
for panel in db.get("panels", []):
    panel_id = panel.get("id")
    if panel_id in [9, 16, 20]:
        safe_print(f"Updating Panel {panel_id}: {panel.get('title')}")
        
        # 1. Update SQL target
        if panel.get("targets"):
            target = panel["targets"][0]
            if panel_id == 9:
                target["rawSql"] = f"{select_fields} WHERE OK_NOK = 'OK' ORDER BY id DESC"
            elif panel_id == 16:
                target["rawSql"] = f"{select_fields} WHERE OK_NOK = 'NOK' ORDER BY id DESC"
            elif panel_id == 20:
                target["rawSql"] = f"{select_fields} WHERE ('${{selected_bastidor:raw}}' = 'ALL' OR NBASTIDOR = '${{selected_bastidor:raw}}') ORDER BY NSECUENCIA ASC, id DESC"
        
        # 2. Update fieldOverrides
        if "fieldConfig" in panel and "overrides" in panel["fieldConfig"]:
            for override in panel["fieldConfig"]["overrides"]:
                matcher = override.get("matcher", {})
                if matcher.get("id") == "byName":
                    options = matcher.get("options")
                    if options == "ID":
                        matcher["options"] = "id"
                        safe_print("  Updated override matcher option from 'ID' to 'id'")
                    elif options == "Resultado":
                        matcher["options"] = "OK_NOK"
                        safe_print("  Updated override matcher option from 'Resultado' to 'OK_NOK'")
                    elif options == "Nº Sec":
                        matcher["options"] = "NSECUENCIA"
                        safe_print("  Updated override matcher option from 'Nº Sec' to 'NSECUENCIA'")
        
        # 3. Update options.footer.fields
        if "options" in panel and "footer" in panel["options"]:
            footer = panel["options"]["footer"]
            if "fields" in footer:
                for idx, field in enumerate(footer["fields"]):
                    if field == "Resultado":
                        footer["fields"][idx] = "OK_NOK"
                        safe_print("  Updated footer field 'Resultado' to 'OK_NOK'")
        
        # 4. Update options.sortBy
        if "options" in panel and "sortBy" in panel["options"]:
            for sort in panel["options"]["sortBy"]:
                disp = sort.get("displayName")
                if disp == "Fecha Creación":
                    sort["displayName"] = "id"
                    sort["desc"] = True
                    safe_print("  Updated sortBy field 'Fecha Creación' to 'id' (descending)")
                elif disp == "Nº Sec":
                    sort["displayName"] = "NSECUENCIA"
                    safe_print("  Updated sortBy field 'Nº Sec' to 'NSECUENCIA'")

# Write the modified JSON back
with open(dashboard_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

safe_print("registro_dashboard.json successfully updated!")
