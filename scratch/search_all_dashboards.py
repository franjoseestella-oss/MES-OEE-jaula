import os
import json

db_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards"
out = []

for fname in os.listdir(db_dir):
    if not fname.endswith(".json"):
        continue
    fpath = os.path.join(db_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        try:
            db = json.load(f)
        except Exception as e:
            out.append(f"Error loading {fname}: {e}")
            continue
    
    # Check if file has panels
    panels = db.get("panels", [])
    for p in panels:
        p_title = p.get("title", "")
        # Targets
        for target in p.get("targets", []):
            rawSql = target.get("rawSql", "")
            if "NOK" in rawSql or "LOG_TABLA" in rawSql:
                out.append(f"File: {fname} | Panel: {p_title} ({p.get('id')}) | rawSql contains keyword")
        # Collapsed panels
        for cp in p.get("panels", []):
            cp_title = cp.get("title", "")
            for target in cp.get("targets", []):
                rawSql = target.get("rawSql", "")
                if "NOK" in rawSql or "LOG_TABLA" in rawSql:
                    out.append(f"File: {fname} | Panel (nested): {cp_title} ({cp.get('id')}) | rawSql contains keyword")

with open("scratch/search_dashboards_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
