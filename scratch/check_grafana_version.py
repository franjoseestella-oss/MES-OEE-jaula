import urllib.request
import json
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

try:
    req = urllib.request.Request(f"{GRAFANA_URL}/api/health", headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Health API:")
        print(data)
except Exception as e:
    print("Health error:", e)

try:
    req = urllib.request.Request(f"{GRAFANA_URL}/api/login-ping", headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Login-ping API:")
        print(data)
except Exception as e:
    print("Login-ping error:", e)
