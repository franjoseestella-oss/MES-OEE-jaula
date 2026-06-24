import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

data["time"] = {
    "from": "now/d+7h",
    "to": "now/d+15h"
}

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Successfully restored relative time range in plan_dashboard.json")
