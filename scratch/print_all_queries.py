import json

path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\plan_dashboard.json"

with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

out_lines = []

for p in db.get("panels", []):
    out_lines.append(f"=== Panel {p.get('id')}: {p.get('title')} ({p.get('type')}) ===")
    for target in p.get("targets", []):
        out_lines.append(f"  RefID: {target.get('refId')}")
        out_lines.append(target.get("rawSql", ""))
        out_lines.append("-" * 40)
    # If it's a row, check row panels
    for collapsed_p in p.get("panels", []):
        out_lines.append(f"  === Inner Panel {collapsed_p.get('id')}: {collapsed_p.get('title')} ({collapsed_p.get('type')}) ===")
        for target in collapsed_p.get("targets", []):
            out_lines.append(f"    RefID: {target.get('refId')}")
            out_lines.append(target.get("rawSql", ""))
            out_lines.append("  " + "-" * 40)

with open("scratch/all_queries.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
