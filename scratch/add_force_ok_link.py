import json

file_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\registro_dashboard.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

updated = False
for panel in data.get("panels", []):
    if panel.get("id") == 16:
        # Find overrides
        field_config = panel.setdefault("fieldConfig", {})
        overrides = field_config.setdefault("overrides", [])
        
        # Look for the override matching OK_NOK
        ok_nok_override = None
        for override in overrides:
            matcher = override.get("matcher", {})
            if matcher.get("id") == "byName" and matcher.get("options") == "OK_NOK":
                ok_nok_override = override
                break
        
        if ok_nok_override is None:
            # Create it if it doesn't exist
            ok_nok_override = {
                "matcher": {
                    "id": "byName",
                    "options": "OK_NOK"
                },
                "properties": []
            }
            overrides.append(ok_nok_override)
            
        # Add links property
        properties = ok_nok_override.setdefault("properties", [])
        # Remove any existing links override for OK_NOK to prevent duplication
        properties = [p for p in properties if p.get("id") != "links"]
        
        properties.append({
            "id": "links",
            "value": [
                {
                    "targetBlank": False,
                    "title": "Forzar a OK",
                    "url": "http://localhost:8000/api/v1/sequences/${__data.fields.id}/force-ok"
                }
              ]
        })
        ok_nok_override["properties"] = properties
        updated = True
        print("Updated panel 16 with Forzar a OK link.")
        break

if updated:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("registro_dashboard.json updated successfully.")
else:
    print("Panel 16 not found!")
