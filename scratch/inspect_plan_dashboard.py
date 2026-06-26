import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Title:", data.get("title"))
print("UID:", data.get("uid"))
panels = data.get("panels", [])
print(f"Number of panels: {len(panels)}")
for i, p in enumerate(panels):
    print(f"Index {i}: ID {p.get('id')} - Title: '{p.get('title')}' - Type: '{p.get('type')}'")
