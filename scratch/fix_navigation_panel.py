import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

print(f"Reading {filepath}...")
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

for panel in db.get("panels", []):
    # 1. Update Calendar panel (title: 📅 CALENDARIO LABORAL Y PLANIFICACIÓN DE UNIDADES)
    if panel.get("title") == "📅 CALENDARIO LABORAL Y PLANIFICACIÓN DE UNIDADES":
        print("Moving calendar panel to y=20")
        panel["gridPos"] = {
            "h": 10,
            "w": 24,
            "x": 0,
            "y": 20
        }
    
    # 2. Update Button panel (type: text, content contains /d/panel-oee-mes-fabrica)
    elif panel.get("type") == "text" and "/d/panel-oee-mes-fabrica" in str(panel.get("options", {}).get("content", "")):
        print("Moving button panel below the calendar table (y=30) and formatting the button content")
        panel["gridPos"] = {
            "h": 2,
            "w": 4,
            "x": 0,
            "y": 30
        }
        panel["options"]["content"] = """<div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; font-family: 'Inter', -apple-system, sans-serif; background: transparent; padding: 0; margin: 0;">
  <a href="/d/panel-oee-mes-fabrica" style="display: block; width: 90%; text-align: center; background: #a855f7; color: #ffffff; text-decoration: none; padding: 12px 10px; font-weight: 700; border-radius: 6px; font-size: 0.9rem; transition: all 0.2s ease; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 14px rgba(168, 85, 247, 0.4); line-height: 1.3;"
     onmouseover="this.style.background='#b566ff'; this.style.boxShadow='0 6px 20px rgba(168, 85, 247, 0.6)'; this.style.transform='translateY(-1px)';"
     onmouseout="this.style.background='#a855f7'; this.style.boxShadow='0 4px 14px rgba(168, 85, 247, 0.4)'; this.style.transform='translateY(0)';">
    Volver al<br>Inicio
  </a>
</div>"""

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully updated plan_dashboard.json!")
