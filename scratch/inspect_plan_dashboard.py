import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    data = json.load(f)

lines = []
lines.append("Title: " + str(data.get("title")))
lines.append("UID: " + str(data.get("uid")))
panels = data.get("panels", [])
lines.append(f"Number of panels: {len(panels)}")
for i, p in enumerate(panels):
    lines.append(f"Index {i}: ID {p.get('id')} - Title: '{p.get('title')}' - Type: '{p.get('type')}'")

with open("scratch/inspect_plan_dashboard_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

