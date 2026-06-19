import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

# 1) Add style: dark
d["style"] = "dark"
print("Style set to dark.")

# 2) Find Panel 5 and update rawSql
panel5 = None
for panel in d["panels"]:
    if panel.get("id") == 5:
        panel5 = panel
        break

if panel5:
    sql = panel5["targets"][0]["rawSql"]
    old_clause = "WHERE TRY_CAST(erp.fecha_montaje AS DATE) BETWEEN @Monday AND @Friday;"
    new_clause = """WHERE 
    (TRY_CAST(erp.fecha_montaje AS DATE) BETWEEN @Monday AND @Friday)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday AND log.id IS NULL)
    OR (TRY_CAST(erp.fecha_montaje AS DATE) < @Monday 
        AND log.id IS NOT NULL 
        AND TRY_CAST(CAST(COALESCE(log.FECHA_HORA_FIN_SEC, log.FECHA_HORA_INICIO_SEC) AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) BETWEEN @Monday AND @Friday);"""
    
    if old_clause in sql:
        panel5["targets"][0]["rawSql"] = sql.replace(old_clause, new_clause)
        print("SQL query updated successfully.")
    else:
        print("Target WHERE clause not found in SQL!")
else:
    print("Panel 5 not found!")

# Save back
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print("File saved successfully.")
