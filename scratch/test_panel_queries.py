import json
import urllib.request
import urllib.error
import base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Query endpoint in Grafana
url = f"{GRAFANA_URL}/api/ds/query"

# We will test a query by sending a POST request to Grafana query API
# The datasource UID is 'mes_sqlserver'
# Let's construct a payload that simulates the panel query for Panel 102
payload = {
    "queries": [
        {
            "datasource": {
                "type": "mssql",
                "uid": "mes_sqlserver"
            },
            "rawSql": """
            SELECT 
              10 AS [threshold_min], 90 AS [threshold_max],
              AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) 
                THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0)) * 100.0 
                ELSE 50.0 END) AS [Elevación Con Carga],
              AVG(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) 
                THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0)) * 100.0 
                ELSE 50.0 END) AS [Elevación Sin Carga],
              AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) 
                THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0)) * 100.0 
                ELSE 50.0 END) AS [Descenso Con Carga],
              AVG(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) > COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) 
                THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0)) * 100.0 
                ELSE 50.0 END) AS [Descenso Sin Carga]
            FROM LOG_TABLA 
            WHERE OK_NOK = 'OK'
              AND (NMODELO LIKE 'FD%' OR NMODELO LIKE 'FG%')
              AND fecha_creacion >= '2026-01-01T00:00:00Z'
            """,
            "refId": "A",
            "format": "table"
        }
    ],
    "from": "now-30d",
    "to": "now"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Success! Data columns:")
        frames = res.get("results", {}).get("A", {}).get("frames", [])
        if frames:
            schema = frames[0].get("schema", {})
            fields = schema.get("fields", [])
            print([f.get("name") for f in fields])
        else:
            print("No frames returned.")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
except Exception as e:
    print("Error:", e)
