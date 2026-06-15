import json

registro_path = "grafana/provisioning/dashboards/registro_dashboard.json"

with open(registro_path, "r", encoding="utf-8") as f:
    db = json.load(f)

modified = False

def update_queries(obj):
    global modified
    if isinstance(obj, dict):
        if "rawSql" in obj and isinstance(obj["rawSql"], str):
            sql = obj["rawSql"]
            if "fecha_creacion AS [Fecha Creación]" in sql and "FECHA_MONTAJE" not in sql:
                new_sql = sql.replace(
                    "fecha_creacion AS [Fecha Creación],",
                    "fecha_creacion AS [Fecha Creación], COALESCE(CONVERT(varchar(10), TRY_CAST(FECHA_MONTAJE AS DATE), 103), '') AS [Fecha Montaje],"
                )
                if new_sql != sql:
                    obj["rawSql"] = new_sql
                    print(f"Updated rawSql in object: {obj.get('refId')}")
                    modified = True
        else:
            for k, v in obj.items():
                update_queries(v)
    elif isinstance(obj, list):
        for item in obj:
            update_queries(item)

update_queries(db)

if modified:
    with open(registro_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Updated registro_dashboard.json successfully.")
else:
    print("No changes made to registro_dashboard.json.")
