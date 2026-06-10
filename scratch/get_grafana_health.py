import urllib.request
import json
try:
    with urllib.request.urlopen("http://localhost:3010/api/health") as r:
        print(r.read().decode())
except Exception as e:
    print(f"Error: {e}")
