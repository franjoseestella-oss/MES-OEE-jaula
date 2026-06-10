import json, urllib.request, base64

auth = base64.b64encode(b'fran.jose.estella@gmail.com:admin123').decode()
payload = {
    "queries": [{
        "refId": "A",
        "datasource": {"uid": "mes_sqlserver"},
        "rawSql": "SELECT TIEMPO_ELEVACION_MEDIDO_SINCARGA as elev_med, TIEMPO_ELEVACION_MIN_SINCARGA as elev_min, TIEMPO_ELEVACION_MAX_SINCARGA as elev_max, TIEMPO_DESCENSO_MEDIDO_SINCARGA as desc_med, TIEMPO_DESCENSO_MIN_SINCARGA as desc_min, TIEMPO_DESCENSO_MAX_SINCARGA as desc_max FROM LOG_TABLA WHERE id=12",
        "format": "table"
    }],
    "from": "now-1y",
    "to": "now"
}
data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    "http://localhost:3010/api/ds/query",
    data=data,
    headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode("utf-8"))

frames = result.get("results", {}).get("A", {}).get("frames", [])
if frames:
    schema = frames[0]["schema"]["fields"]
    values = frames[0]["data"]["values"]
    for i, field in enumerate(schema):
        name = field["name"]
        val = values[i][0] if values[i] else None
        print(f"{name}: {val}")
else:
    print("No frames:", json.dumps(result, indent=2)[:500])
