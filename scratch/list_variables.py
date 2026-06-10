import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

templating = db.get("templating", {})
print("Variables in dashboard:")
for var in templating.get("list", []):
    print(f"Name: {var.get('name')} | Type: {var.get('type')} | Label: {var.get('label')}")
