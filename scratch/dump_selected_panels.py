import json
import sys

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

output_data = {}
for pid in [4, 10]:
    panel = next((p for p in db.get("panels", []) if p.get("id") == pid), None)
    if panel:
        output_data[str(pid)] = panel

with open("scratch/panels_4_10.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
print("Saved panels 4 and 10 to scratch/panels_4_10.json")
