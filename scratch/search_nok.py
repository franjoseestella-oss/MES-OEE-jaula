import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    targets = p.get("targets", [])
    for target in targets:
        rawSql = target.get("rawSql", "")
        if "NOK" in rawSql:
            print(f"Panel ID {p.get('id')} ({p.get('title')}): rawSql contains 'NOK'")
    
    # Check overrides
    fieldConfig = p.get("fieldConfig", {})
    defaults = fieldConfig.get("defaults", {})
    overrides = fieldConfig.get("overrides", [])
    for override in overrides:
        for prop in override.get("properties", []):
            if "mappings" in prop.get("id", ""):
                val_str = json.dumps(prop.get("value", ""))
                if "NOK" in val_str:
                    print(f"Panel ID {p.get('id')} ({p.get('title')}): override contains 'NOK'")
