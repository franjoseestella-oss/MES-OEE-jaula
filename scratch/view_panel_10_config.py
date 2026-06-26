import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    if p.get("id") == 10:
        # print config keys and some relevant structures
        print("Panel 10 title:", p.get("title"))
        print("Panel 10 type:", p.get("type"))
        print("Panel 10 timeShift:", p.get("timeShift"))
        print("Panel 10 timeFrom:", p.get("timeFrom"))
        # Print options, custom, overrides, etc.
        print("Panel 10 fieldConfig:", json.dumps(p.get("fieldConfig", {}), indent=2))
        print("Panel 10 options:", json.dumps(p.get("options", {}), indent=2))
