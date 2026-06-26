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
                
                # Check if already updated
                if "@TheoreticalActiveSlotIdx" in sql:
                    print("Panel 10 query is already updated or contains @TheoreticalActiveSlotIdx.")
                    updated = True
                    break
                
                # 1. Add TheoreticalActiveSlotIdx declaration and calculation
                old_active_slot_calc = """-- Find active slot index in progress
DECLARE @ActiveSlotIdx INT;
SELECT @ActiveSlotIdx = MIN(slot_idx)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;"""

                new_active_slot_calc = """-- Find active slot index in progress
DECLARE @ActiveSlotIdx INT;
SELECT @ActiveSlotIdx = MIN(slot_idx)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;

-- Find theoretical active slot index
DECLARE @TheoreticalActiveSlotIdx INT;
SELECT TOP 1 @TheoreticalActiveSlotIdx = slot_idx
FROM #SeqsToSchedule
WHERE planned_start <= @CurrentProgressTime AND planned_end >= @CurrentProgressTime;

IF @TheoreticalActiveSlotIdx IS NULL
BEGIN
    SELECT @TheoreticalActiveSlotIdx = COALESCE(
        (SELECT MAX(slot_idx) FROM #SeqsToSchedule WHERE planned_start <= @CurrentProgressTime),
        1
    );
END;"""

                # 2. Modify rule condition in FilteredTimestamps and Active states SELECT
                old_rule_cond = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL THEN"
                new_rule_cond = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL AND @ActiveSlotIdx >= @TheoreticalActiveSlotIdx THEN"

                if old_active_slot_calc in sql and old_rule_cond in sql:
                    sql = sql.replace(old_active_slot_calc, new_active_slot_calc)
                    sql = sql.replace(old_rule_cond, new_rule_cond)
                    target["rawSql"] = sql
                    print("Updated Panel 10 query in plan_dashboard.json.")
                    updated = True
                else:
                    print("Error: Could not find target patterns in Panel 10 query.")
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
