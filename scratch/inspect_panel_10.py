import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 9:
        print("--- PANEL 9 ---")
        print("Panel Title:", p.get("title"))
        print("Targets:")
        for target in p.get("targets", []):
            print("  Format:", target.get("format"))
            print("  RawSQL:", target.get("rawSql"))
        print("Transformations:")
        print(json.dumps(p.get("transformations", []), indent=2))
        print("Options:")
        print(json.dumps(p.get("options", {}), indent=2))
        break
