import os
import httpx
import json

GRAFANA_URL = "http://localhost:3010"
TOKEN = os.environ.get("GRAFANA_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

query = """
DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST($__timeFrom() AS DATE), 112);

IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
BEGIN
    SET @ActiveDate = COALESCE(
        (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
        (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
        (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
    );
END;

SELECT @ActiveDate AS ActiveDate;
"""

payload = {
    "queries": [
        {
            "refId": "A",
            "datasource": {
                "type": "mssql",
                "uid": "mes_sqlserver"
            },
            "rawSql": query,
            "format": "table"
        }
    ],
    "from": "now/d+7h",
    "to": "now/d+15h"
}

r = httpx.post(f"{GRAFANA_URL}/api/ds/query", json=payload, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    res = r.json()
    print("Executed Query String:")
    print(res.get("results", {}).get("A", {}).get("frames", [{}])[0].get("schema", {}).get("meta", {}).get("executedQueryString"))
    print("\nData values:")
    print(res.get("results", {}).get("A", {}).get("frames", [{}])[0].get("data", {}).get("values"))
else:
    print(r.text)
