import urllib.request
import json
import base64

headers = {
    'Authorization': 'Basic ' + base64.b64encode(b'fran.jose.estella@gmail.com:admin123').decode(),
}
req = urllib.request.Request('http://localhost:3010/api/search?type=dash-db', headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    for db in data:
        print(f"ID: {db.get('id')}, UID: {db.get('uid')}, Title: {db.get('title')}, URI: {db.get('uri')}")
