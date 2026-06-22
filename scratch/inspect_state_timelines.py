import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/turno_actual_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("type") == "state-timeline":
        print("Panel Title:", p.get("title"))
        print("Panel ID:", p.get("id"))
        print("Targets:")
        for target in p.get("targets", []):
            print("  Format:", target.get("format"))
            print("  RawSQL:", target.get("rawSql"))
        print("Transformations:")
        print(json.dumps(p.get("transformations", []), indent=2))
        print("Options:")
        print(json.dumps(p.get("options", {}), indent=2))
        print("---")
