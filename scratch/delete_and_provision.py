import urllib.request
import json
import base64
import time

headers = {
    'Authorization': 'Basic ' + base64.b64encode(b'fran.jose.estella@gmail.com:admin123').decode(),
}

# 1. Delete dashboard via API
req = urllib.request.Request(
    'http://localhost:3010/api/dashboards/uid/mes-log-v1',
    headers=headers,
    method='DELETE'
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print("Delete response:", result)
except urllib.error.HTTPError as e:
    print(f"Error deleting dashboard: {e.code} - {e.read().decode('utf-8')}")

# 2. Wait 5 seconds for provisioning scan
print("Waiting 5 seconds for provisioning scan...")
time.sleep(5)

# 3. Check if dashboard has been re-imported
req = urllib.request.Request('http://localhost:3010/api/dashboards/uid/mes-log-v1', headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Re-imported successfully!")
        print("Version:", data.get('dashboard', {}).get('version'))
        for p in data.get('dashboard', {}).get('panels', []):
            if p.get('id') == 15:
                print("Panel 15 SQL query contains Límite Máximo Gauge:", 'Límite Máximo Gauge' in p.get('targets', [{}])[0].get('rawSql', ''))
                print("Transformations count:", len(p.get('transformations', [])))
except urllib.error.HTTPError as e:
    print(f"Error fetching dashboard after delete: {e.code} - {e.read().decode('utf-8')}")
