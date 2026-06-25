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
                
                old_case = """            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN
                CASE 
                    WHEN ft.t >= s.planned_end THEN 'Exceso de tiempo'
                    ELSE 'En proceso'
                END"""
                
                new_case = """            WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end) THEN
                CASE 
                    WHEN ft.t < s.planned_start OR ft.t >= s.planned_end THEN 'Exceso de tiempo'
                    ELSE 'En proceso'
                END"""
                
                if old_case in sql:
                    target["rawSql"] = sql.replace(old_case, new_case)
                    print("Updated Panel 10 query with early-start grey coloring.")
                    updated = True
                else:
                    print("Error: Could not find target case block in Panel 10 query.")
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
