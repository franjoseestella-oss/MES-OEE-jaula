import os
import httpx
import json

GRAFANA_URL = "http://localhost:3010"
TOKEN = os.environ.get("GRAFANA_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def check():
    r = httpx.get(f"{GRAFANA_URL}/api/datasources", headers=headers)
    print("Status:", r.status_code)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r.text)

if __name__ == "__main__":
    check()
