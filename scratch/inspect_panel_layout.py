import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"{'ID':<5} | {'Title':<45} | {'gridPos':<20}")
print("-" * 80)
for panel in data.get("panels", []):
    title = panel.get("title", "")
    pid = panel.get("id")
    grid = panel.get("gridPos", {})
    grid_str = f"h:{grid.get('h')} w:{grid.get('w')} x:{grid.get('x')} y:{grid.get('y')}"
    print(f"{pid:<5} | {title[:45]:<45} | {grid_str:<20}")
