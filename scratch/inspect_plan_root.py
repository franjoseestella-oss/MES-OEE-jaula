import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

print("Title:", db.get("title"))
print("Refresh:", db.get("refresh"))
print("Timepicker:", db.get("timepicker"))
print("Time:", db.get("time"))
