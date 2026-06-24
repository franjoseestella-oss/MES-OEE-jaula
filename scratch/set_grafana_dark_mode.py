import urllib.request
import base64
import json

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

def set_pref(endpoint):
    url = f"{GRAFANA_URL}{endpoint}"
    payload = {"theme": "dark"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Preferences updated successfully at {endpoint}: {resp.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error updating preferences at {endpoint}: {e}")

if __name__ == "__main__":
    set_pref("/api/org/preferences")
    set_pref("/api/user/preferences")
