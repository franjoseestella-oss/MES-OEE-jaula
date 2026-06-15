import os
import json

dashboards_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards"
output_file = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\queries_output.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for filename in os.listdir(dashboards_dir):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(dashboards_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        out.write(f"=== {filename} ===\n")
        panels = data.get("panels", [])
        for p in panels:
            title = p.get("title", "")
            targets = p.get("targets", [])
            for t in targets:
                rawSql = t.get("rawSql", "")
                if rawSql:
                    out.write(f"Panel: {title}\n")
                    out.write(rawSql + "\n")
                    out.write("-" * 80 + "\n")
