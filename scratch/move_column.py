import json

file_path = "grafana/provisioning/dashboards/registro_dashboard.json"

with open(file_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

changed_panels = 0
for panel in db.get("panels", []):
    title = panel.get("title", "")
    for target in panel.get("targets", []):
        if "rawSql" in target:
            sql = target["rawSql"]
            if "OK_NOK AS OK_NOK" in sql and "NBASTIDOR AS NBASTIDOR" in sql:
                safe_title = title.encode('ascii', 'replace').decode()
                print(f"Modifying query for panel: {safe_title}")
                # Remove it from the end
                sql = sql.replace(",\n  OK_NOK AS OK_NOK\nFROM LOG_TABLA", "\nFROM LOG_TABLA")
                # Insert it after NBASTIDOR
                sql = sql.replace("\n  NBASTIDOR AS NBASTIDOR,\n  NMASTIL AS NMASTIL,", "\n  NBASTIDOR AS NBASTIDOR,\n  OK_NOK AS OK_NOK,\n  NMASTIL AS NMASTIL,")
                target["rawSql"] = sql
                changed_panels += 1

print(f"Modified {changed_panels} panels.")

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Saved updated dashboard JSON to file.")
