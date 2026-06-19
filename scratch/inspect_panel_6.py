import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    if p.get("id") == 6:
        text = json.dumps(p, indent=2, ensure_ascii=False)
        print(text.encode('ascii', 'replace').decode('ascii'))
