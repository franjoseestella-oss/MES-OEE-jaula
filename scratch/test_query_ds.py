import os
import httpx
import json

GRAFANA_URL = "http://localhost:3010"
TOKEN = os.environ.get("GRAFANA_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def check_query():
    payload = {
        "queries": [
            {
                "refId": "A",
                "datasource": {
                    "type": "mssql",
                    "uid": "mes_sqlserver"
                },
                "rawSql": "SELECT TOP 3 id, fecha_creacion, TIEMPO_ELEVACION_MEDIDO_SINCARGA FROM LOG_TABLA ORDER BY fecha_creacion DESC",
                "format": "table"
            }
        ],
        "from": "now-24h",
        "to": "now"
    }
    
    r = httpx.post(f"{GRAFANA_URL}/api/ds/query", json=payload, headers=headers)
    print("Status:", r.status_code)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r.text)

if __name__ == "__main__":
    check_query()
