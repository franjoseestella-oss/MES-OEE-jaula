import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    title = panel.get("title", "")
    panel_id = panel.get("id")
    panel_type = panel.get("type")
    grid = panel.get("gridPos", {})
    if any(keyword in title.upper() for keyword in ["OEE", "DISPONIBILIDAD", "RENDIMIENTO", "CALIDAD"]):
        print(f"Panel ID: {panel_id} | Title: '{title}' | Type: {panel_type} | Grid: {grid}")
