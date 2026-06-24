import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Timezone of the dashboard:")
print(data.get("timezone"))
