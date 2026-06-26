import json

try:
    with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
        json.load(f)
    print("VALID JSON")
except Exception as e:
    print("INVALID JSON:", e)
