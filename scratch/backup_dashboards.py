import os
import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

dashboards = {
    "mes-alarms-v1": "alarmas_dashboard.json",
    "mes-oee-v2": "distribuidor_dashboard.json",
    "mes-home-v1": "home_dashboard.json",
    "mes-plan-v1": "plan_dashboard.json",
    "mes-reg-v1": "registro_dashboard.json",
    "panel-oee-mes-fabrica": "turno_actual_dashboard.json"
}

dest_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards"

for uid, filename in dashboards.items():
    url = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"
    print(f"Fetching dashboard {uid}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # The dashboard payload is inside data['dashboard']
            dashboard_model = data["dashboard"]
            
            # Save it formatted nicely
            filepath = os.path.join(dest_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dashboard_model, f, indent=2, ensure_ascii=False)
            print(f"  Successfully saved to {filename}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code} for {uid}: {e.read().decode()}")
    except Exception as e:
        print(f"  Failed for {uid}: {e}")

print("Done!")
