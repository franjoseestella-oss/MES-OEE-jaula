import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "grafana/provisioning/dashboards/registro_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

updated_count = 0
for panel in db.get("panels", []):
    title = panel.get("title")
    pid = panel.get("id")
    for t in panel.get("targets", []):
        raw_sql = t.get("rawSql")
        if raw_sql and "$__timeFilter(FECHA_MONTAJE)" in raw_sql:
            new_sql = raw_sql.replace("$__timeFilter(FECHA_MONTAJE)", "$__timeFilter(FECHA_HORA_FIN_SEC)")
            t["rawSql"] = new_sql
            print(f"Updated Panel ID {pid} ({title})")
            updated_count += 1

if updated_count > 0:
    with open(db_path, "w", encoding="utf-8") as fw:
        json.dump(db, fw, indent=2, ensure_ascii=False)
    print(f"Successfully updated {updated_count} queries locally.")
    
    # Push back to Grafana
    # Strip id to let Grafana match by UID and avoid conflict
    if "id" in db:
        del db["id"]
        
    payload = {
        "dashboard": db,
        "folderUid": "dfovv23tkq48wc",
        "overwrite": True
    }
    auth = ("fran.jose.estella@gmail.com", "admin123")
    url = "http://localhost:3010/api/dashboards/db"
    headers = {"Content-Type": "application/json"}
    
    res = requests.post(url, json=payload, auth=auth, headers=headers)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
else:
    print("No matches of $__timeFilter(FECHA_MONTAJE) found to replace.")
