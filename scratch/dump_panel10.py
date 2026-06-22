import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        with open("scratch/panel10.json", "w", encoding="utf-8") as out:
            json.dump(p, out, indent=2, ensure_ascii=False)
        print("Panel 10 JSON saved to scratch/panel10.json")
        break
else:
    print("Panel 10 not found!")
