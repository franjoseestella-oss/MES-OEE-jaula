import json
import requests
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

db_path = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(db_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Try pushing a few times in case Grafana is still starting up
for attempt in range(5):
    try:
        # Delete dashboard id to overwrite/create clean
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
        print(f"Attempt {attempt+1}: Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        if res.status_code == 200:
            print("Successfully pushed to Grafana.")
            sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
    time.sleep(5)

print("Failed to push dashboard after 5 attempts.")
sys.exit(1)
