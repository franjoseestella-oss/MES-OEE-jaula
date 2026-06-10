import json
import urllib.request
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        dashboard = res.get("dashboard", {})
        for p in dashboard.get("panels", []):
            if p.get("id") == 15:
                print("Live Panel 15 fieldConfig:")
                print(json.dumps(p.get("fieldConfig", {}), indent=2, ensure_ascii=False))
                print("\nLive Panel 15 transformations:")
                print(json.dumps(p.get("transformations", []), indent=2, ensure_ascii=False))
                break
except Exception as e:
    print("Error:", e)
