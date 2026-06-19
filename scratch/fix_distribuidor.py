import json

print("Fixing distribuidor_dashboard.json...")
with open("grafana/provisioning/dashboards/distribuidor_dashboard.json", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the time filter macro
content = content.replace("$__timeFilter(TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2))", "$__timeFilter(FECHA_HORA_INICIO_SEC)")

# Load JSON to modify the template variable
db = json.loads(content)
templating = db.get("templating", {})
for var in templating.get("list", []):
    if var.get("name") == "selected_bastidor":
        var["query"] = "SELECT NBASTIDOR FROM (SELECT NBASTIDOR, MAX(id) as max_f FROM LOG_TABLA GROUP BY NBASTIDOR) AS t ORDER BY max_f DESC"
        print("Updated selected_bastidor variable query!")

with open("grafana/provisioning/dashboards/distribuidor_dashboard.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("distribuidor_dashboard.json fixed successfully!")
