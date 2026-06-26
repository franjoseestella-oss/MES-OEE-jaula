import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    if p.get("id") == 10:
        print(json.dumps(p, indent=2, ensure_ascii=False))
