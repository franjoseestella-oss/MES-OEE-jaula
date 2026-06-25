import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

out_path = "scratch/all_plan_queries_dump.txt"
with open(out_path, "w", encoding="utf-8") as out:
    for panel in db.get("panels", []):
        out.write(f"=========================================================\n")
        out.write(f"PANEL ID: {panel.get('id')} | TITLE: {panel.get('title')} | TYPE: {panel.get('type')}\n")
        out.write(f"=========================================================\n")
        for target in panel.get("targets", []):
            ref_id = target.get("refId", "")
            sql = target.get("rawSql", "")
            out.write(f"--- TARGET {ref_id} ---\n")
            out.write(sql)
            out.write("\n\n")

print(f"Dumped all plan queries (all targets) to {out_path}")
