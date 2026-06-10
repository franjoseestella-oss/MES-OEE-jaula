import json

file_path = "grafana/provisioning/dashboards/log_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Find Panel 9 (OK) and Panel 16 (NOK)
p9 = None
p16 = None
for p in db.get("panels", []):
    if p.get("id") == 9:
        p9 = p
    elif p.get("id") == 16:
        p16 = p

if not p9 or not p16:
    raise ValueError("Panel 9 or Panel 16 not found in dashboard json")

# Update titles with visual color indicators
p9["title"] = "🟢 REGISTRO DETALLADO DE PRUEBAS OK"
p16["title"] = "🔴 REGISTRO DETALLADO DE PRUEBAS NOK"

# Update overrides for "Resultado" column to use color-background cell display mode
def update_resultado_override(panel):
    overrides = panel.get("fieldConfig", {}).get("overrides", [])
    for override in overrides:
        if override.get("matcher", {}).get("options") == "Resultado":
            properties = override.get("properties", [])
            # Check if custom.cellOptions is already there
            has_cell_options = False
            for prop in properties:
                if prop.get("id") == "custom.cellOptions":
                    prop["value"] = {"type": "color-background"}
                    has_cell_options = True
                    break
            if not has_cell_options:
                properties.append({
                    "id": "custom.cellOptions",
                    "value": {
                        "type": "color-background"
                    }
                })

update_resultado_override(p9)
update_resultado_override(p16)

# Write back to file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Successfully updated titles and Resultado cell options in log_dashboard.json!")
