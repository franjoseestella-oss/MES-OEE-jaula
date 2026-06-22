import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

auth = ("fran.jose.estella@gmail.com", "admin123")
url = "http://localhost:3010/api/dashboards/uid/mes-plan-v1"
res = requests.get(url, auth=auth)
if res.status_code != 200:
    print(f"Failed to get live dashboard: {res.status_code} - {res.text}")
    sys.exit(1)

live_dash = res.json().get("dashboard", {})
for p in live_dash.get("panels", []):
    if p.get("id") == 10:
        print("Live Panel ID 10 details:")
        print("Title:", p.get("title"))
        print("Type:", p.get("type"))
        print("Targets:")
        for target in p.get("targets", []):
            print("  Format:", target.get("format"))
            print("  RawSQL length:", len(target.get("rawSql", "")))
        print("Transformations:")
        print(json.dumps(p.get("transformations", []), indent=2))
        print("Options:")
        print(json.dumps(p.get("options", {}), indent=2))
        break
else:
    print("Live panel 10 not found")
