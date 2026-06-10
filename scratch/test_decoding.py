import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "rb") as f:
    content = f.read()

decoded = content.decode("utf-8", errors="ignore")
db = json.loads(decoded)

for p in db.get("panels", []):
    if p.get("id") == 9:
        print("Panel 9 Title:", p.get("title"))
        query = p.get("targets", [{}])[0].get("rawSql", "")
        print("Raw query:", query)
        print("UTF-8 decoded query bytes:", query.encode("utf-8"))
        break
