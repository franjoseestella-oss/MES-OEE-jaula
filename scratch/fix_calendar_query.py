import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

print(f"Reading {filepath}...")
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

updated = False
for panel in db.get("panels", []):
    if panel.get("title") == "📅 CALENDARIO LABORAL Y PLANIFICACIÓN DE UNIDADES":
        print("Found panel!")
        for target in panel.get("targets", []):
            raw_sql = target.get("rawSql", "")
            print(f"Original SQL:\n{raw_sql}")
            # Remove WHERE $__timeFilter(Fecha)
            # Make sure we handle potential variations in spacing or newlines
            new_sql = raw_sql.replace("WHERE $__timeFilter(Fecha)", "").replace("WHERE\n  $__timeFilter(Fecha)", "")
            # Also clean up any double spaces/newlines left behind
            new_sql = "\n".join([line for line in new_sql.splitlines() if line.strip() != ""])
            target["rawSql"] = new_sql
            print(f"New SQL:\n{new_sql}")
            updated = True

if updated:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Successfully updated plan_dashboard.json!")
else:
    print("Could not find or update panel.")
