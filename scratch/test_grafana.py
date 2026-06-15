import os
import httpx
import json

GRAFANA_URL = "http://localhost:3010"
TOKEN = os.environ.get("GRAFANA_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test():
    try:
        # Check health
        r = httpx.get(f"{GRAFANA_URL}/api/health")
        print("Health Status:", r.status_code, r.text)
        
        # Check folders/dashboards search
        r = httpx.get(f"{GRAFANA_URL}/api/search", headers=headers)
        print("Search Status:", r.status_code)
        if r.status_code == 200:
            print("Dashboards/Folders found:")
            print(json.dumps(r.json(), indent=2))
        else:
            print("Search Error:", r.text)

    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test()
