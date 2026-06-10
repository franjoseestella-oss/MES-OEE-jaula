import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for pid in [10, 11, 12, 13]:
    for panel in db.get("panels", []):
        if panel.get("id") == pid:
            print(f"--- Panel {pid} config ---")
            print(json.dumps(panel, indent=2))
