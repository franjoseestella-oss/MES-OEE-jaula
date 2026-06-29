import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    db = json.load(f)

panels = {p["id"]: p for p in db.get("panels", [])}

output_path = "scratch/dumped_panel_queries.txt"
with open(output_path, "w", encoding="utf-8") as out:
    for pid in [4, 5, 10]:
        if pid in panels:
            raw_sql = panels[pid]["targets"][0]["rawSql"]
            out.write(f"=== Panel {pid} ===\n{raw_sql}\n\n")

print(f"Dumped to {output_path}")
