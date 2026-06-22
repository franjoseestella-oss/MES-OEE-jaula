import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dash = json.load(f)

for p in dash.get("panels", []):
    if p.get("id") == 10:
        print("Panel Title:", p.get("title"))
        print("Panel Type:", p.get("type"))
        print("Targets:")
        for target in p.get("targets", []):
            print("  RefId:", target.get("refId"))
            print("  Datasource:", target.get("datasource"))
            print("  RawSQL:")
            print(target.get("rawSql"))
        print("Options:")
        print(json.dumps(p.get("options", {}), indent=2))
        print("FieldConfig:")
        print(json.dumps(p.get("fieldConfig", {}), indent=2))
        break
