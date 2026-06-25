import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

updated = False
for panel in db.get("panels", []):
    if panel.get("id") == 10:
        for target in panel.get("targets", []):
            if target.get("refId") == "A":
                sql = target.get("rawSql")
                old_where = "WHERE bt.t >= s.planned_start"
                new_where = """WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END"""
                if old_where in sql:
                    target["rawSql"] = sql.replace(old_where, new_where)
                    print("Updated Panel 10 query in plan_dashboard.json.")
                    updated = True
                else:
                    print("Error: Could not find target where clause in Panel 10 query.")
                break
        break

if not updated:
    print("Error: Panel 10 query not updated.")
    sys.exit(1)

with open(db_path, "w", encoding="utf-8") as fw:
    json.dump(db, fw, indent=2, ensure_ascii=False)

# Push to Grafana API
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
print(f"Grafana API Push Status Code: {res.status_code}")
print(f"Response: {res.text}")
