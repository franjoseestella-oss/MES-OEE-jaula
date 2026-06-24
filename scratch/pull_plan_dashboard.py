import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"
UID = "mes-plan-v1"
FILEPATH = "grafana/provisioning/dashboards/plan_dashboard.json"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

def main():
    req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{UID}", headers=headers)
    with urllib.request.urlopen(req_get) as resp_get:
        existing = json.loads(resp_get.read().decode("utf-8"))
        final_dashboard = existing["dashboard"]
        
    with open(FILEPATH, "w", encoding="utf-8") as fw:
        json.dump(final_dashboard, fw, indent=2, ensure_ascii=False)
    print("Successfully pulled and updated plan_dashboard.json")

if __name__ == "__main__":
    main()
